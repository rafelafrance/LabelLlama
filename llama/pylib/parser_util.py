import importlib
import logging
import re
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar

import pandas as pd
import yaml

from llama.pylib.ocr_util import MIN_SIZE, OcrDocs, OcrResult

FIELD_PROMPT_DIR = Path("prompts")

FIRST_COLUMNS = ["status", "source", "text", "elapsed"]

# Regexes for getting the sections of a prompt markdown
SYS_PROMPT = re.compile(r"^Base\s+Prompt", flags=re.IGNORECASE)
LLM_FIELDS = re.compile(r"^LLM\s+Fields", flags=re.IGNORECASE)
CALC_FIELDS = re.compile(r"^Calculated\s+Fields", flags=re.IGNORECASE)


def get_front_yaml(text: str, path: Path) -> dict:
    top = re.search("^---$.*^---$", text, flags=re.MULTILINE | re.DOTALL)
    if not top:
        raise ValueError(f"Improperly formatted prompt file. {path}")

    top = top.group(0).replace("---", "")
    front = yaml.safe_load(top)
    return front


class ParseStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "ERROR"
    UNKNOWN = ""


@dataclass
class FieldPrompt:
    name: str
    description: str
    module: Path
    columns: list[str] = field(default_factory=list[str])
    prompts: list[str] = field(default_factory=list[str])

    @classmethod
    def load(cls, link: str) -> FieldPrompt:
        path = FIELD_PROMPT_DIR / link
        with path.open() as f:
            text = f.read()

        front = get_front_yaml(text, path)

        sections = re.split(r"^(?<!#)#\sPrompt\s+(\w+)$", text, flags=re.MULTILINE)
        columns, prompts = [], []
        for column, prompt in zip(sections[1::2], sections[2::2], strict=True):
            columns.append(column.strip())
            prompts.append(prompt.strip())

        field_prompt = cls(
            name=front["name"],
            description=front["description"],
            module=Path(front["module"]),
            columns=columns,
            prompts=prompts,
        )

        return field_prompt

    def field_class(self) -> Any:
        cls_name = self.name[0].upper() + self.name[1:]
        mod_name = str(self.module).removesuffix(".py").replace("/", ".")
        module = importlib.import_module(mod_name)
        cls = getattr(module, cls_name)
        return cls


@dataclass
class PromptFileParser:
    name: str = ""
    description: str = ""
    base_prompt: str = ""
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    calc_fields: dict[str, str] = field(default_factory=dict[str, str])

    @classmethod
    def load(cls, prompt_path: Path) -> PromptFileParser:
        with prompt_path.open() as f:
            text = f.read()

        front = get_front_yaml(text, prompt_path)

        # Split Markdown file into sections using headers
        sections = re.split(r"^(?<!#)#\s", text, flags=re.MULTILINE)

        sys_prompt = ""
        fields, calc_fields = {}, {}

        for section in sections:
            section = section.strip()

            # Get system prompt section
            if SYS_PROMPT.match(section):
                sys_prompt = SYS_PROMPT.sub("", section).strip()

            # Get output LLM fields list section
            elif LLM_FIELDS.match(section):
                section = LLM_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/]+\.md\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    fields[lnk] = FieldPrompt.load(lnk)

            elif CALC_FIELDS.match(section):
                section = CALC_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/]+\.py\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    calc_fields[lnk] = None

        prompt = cls(
            name=front["name"],
            description=front["description"],
            base_prompt=sys_prompt,
            fields=fields,
            calc_fields=calc_fields,
        )
        return prompt


@dataclass
class ParserArgs:
    prompt: ParserPrompt
    model_name: str = "qwen/qwen3.6-35b-a3b"
    api_host: str = "http://localhost:1234/v1"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout: int = 300
    threads: int = 4


@dataclass
class ParserPrompt:
    # -------------- ClassVars ---------------
    text_prompt: ClassVar[str] = "Extract data from this `text` (str):\n"
    # ----------------------------------------

    name: str
    description: str
    base_prompt: str = ""
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    field_prompts: str = ""
    field_template: str = ""
    _system_prompt: str = ""
    _columns: list[str] = field(default_factory=list[str])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            base_prompt=prompt_parser.base_prompt,
            fields=prompt_parser.fields,
        )
        if prompt.fields:
            prompt.field_prompts = prompt.build_field_prompts()
            prompt.field_template = prompt.build_field_template()

        return prompt

    @property
    def system_prompt(self) -> str:
        if not self._system_prompt:
            self._system_prompt = "\n\n".join(
                [
                    p
                    for p in (self.base_prompt, self.field_prompts, self.field_template)
                    if p
                ]
            )
        return self._system_prompt

    @property
    def column_names(self) -> list[str]:
        """Get all column names."""
        if not self._columns:
            for field_ in self.fields.values():
                self._columns += field_.columns
        return self._columns

    def build_field_prompts(self) -> str:
        formatted = [
            f"{i}. {p}"
            for f in self.fields.values()
            for i, p in enumerate(f.prompts, 1)
        ]
        self.field_prompts = "\n".join(formatted)
        return self.field_prompts

    def build_field_template(self) -> str:
        template = ["Structure all output with the following template."]
        template += [
            f"<< ## {c} ## >>\n{{{c}}}" for f in self.fields.values() for c in f.columns
        ]
        template.append("<< ## completed ## >>")
        self.field_template = "\n\n".join(template)
        return self.field_template

    def log_size(self) -> None:
        sys_prompt = self.system_prompt
        length = len(sys_prompt)
        words = len(sys_prompt.split())
        logging.info(
            f"Prompt lengths (without payload) = {length} characters, {words} words"
        )

    def build_text_prompt(self, text: str) -> str:
        return self.text_prompt + text


@dataclass
class ParsedDocs:
    ocr_file: Path | None = None
    ocr_records: list[OcrResult] = field(default_factory=list[OcrResult])
    parsed_file: Path | None = None
    parsed_file_mode: str = "w"
    parsed_records: list[dict] = field(default_factory=list[dict])
    already_parsed: set[str] = field(default_factory=set[str])
    tasks: list[OcrResult] = field(default_factory=list[OcrResult])
    limit: int | None = None

    @classmethod
    def build(
        cls, parsed_file: Path, ocr_file: Path, limit: int | None = None
    ) -> ParsedDocs:
        docs = cls(parsed_file=parsed_file, ocr_file=ocr_file, limit=limit)

        docs.ocr_records = OcrDocs.get_ocr_records(ocr_file)
        docs.ocr_records = docs.ocr_records[:limit]

        docs.parsed_records, docs.parsed_file_mode = docs.read_parsed_records(
            parsed_file
        )
        docs.already_parsed = docs.get_already_parsed()
        docs.tasks = docs.get_tasks()
        return docs

    def read_parsed_records(self, parsed_file: Path | None) -> tuple[list[dict], str]:
        mode = "w"
        records = []
        if (
            parsed_file
            and parsed_file.exists()
            and parsed_file.stat().st_size >= MIN_SIZE
        ):
            self.parsed_file_mode = "a"
            df = pd.read_csv(parsed_file, dtype=str).fillna("")
            self.parsed_records = df.to_dict("records")
        return records, mode

    def get_already_parsed(self) -> set[str]:
        return {
            r["source"]
            for r in self.parsed_records
            if r["status"] == ParseStatus.SUCCESS
        }

    def get_tasks(self) -> list[OcrResult]:
        return sorted(
            [r for r in self.ocr_records if r.source not in self.already_parsed],
            key=lambda r: r.source,
        )


@dataclass
class ParserCleaner:
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    _field_classes: dict[str, Any] = field(default_factory=dict[str, Any])

    @property
    def field_classes(self) -> dict[str, Any]:
        """Return field classes indexed by column/header name."""
        if not self._field_classes:
            self._field_classes = {
                f.name: f.field_class() for f in self.fields.values()
            }
        return self._field_classes

    @staticmethod
    def llm_reply_to_dict(content: str, columns: list[str]) -> dict:
        """Convert an LM reply in llm_prompt.get_field_template format to a dict."""
        # Get field names and the values
        splits = re.split(r"^<< ## (\w+) ##(?: >>)?$", content, flags=re.MULTILINE)

        # Remove first blank split
        if splits[0].strip() == "":
            splits = splits[1:]

        # Try to match field names with values
        as_dict = {
            k: v.strip()
            for k, v in zip(splits[::2], splits[1::2], strict=False)
            if k in columns
        }

        return as_dict
