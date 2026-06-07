import importlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

FIELD_PROMPT_DIR = Path("prompts") / "fields"

MIN_PROMPT_LEN = 40

# The system prompt section of the prompt
SYS_PROMPT = re.compile(r"^System\s+Prompt", flags=re.IGNORECASE)

# The output fields section of the prompt
OUT_FIELDS = re.compile(r"^Output\s+Fields", flags=re.IGNORECASE)


def get_front_yaml(text: str, path: Path) -> dict:
    top = re.search("^---$.*^---$", text, flags=re.MULTILINE | re.DOTALL)
    if not top:
        raise ValueError(f"Improperly formatted prompt file. {path}")

    top = top.group(0).replace("---", "")
    front = yaml.safe_load(top)
    return front


@dataclass
class FieldPrompt:
    name: str
    description: str
    module: Path
    columns: list[str] = field(default_factory=list)
    prompts: list[str] = field(default_factory=list)

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
class Prompt:
    name: str
    description: str
    system_prompt: str = ""
    field_prompts: dict[str, FieldPrompt] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> Prompt:
        with path.open() as f:
            text = f.read()

        front = get_front_yaml(text, path)

        # Split Markdown file into sections using headers
        sections = re.split(r"^(?<!#)#\s", text, flags=re.MULTILINE)

        sys_prompt = ""
        fields = {}
        for section in sections:
            section = section.strip()

            # Get system prompt section
            if SYS_PROMPT.match(section):
                sys_prompt = SYS_PROMPT.sub("", section).strip()

            # Get output fields list section
            elif OUT_FIELDS.match(section):
                section = OUT_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/]+\.md\)", section)
                for link in links:
                    link = link.removeprefix("(").removesuffix(")")
                    fields[link] = FieldPrompt.load(link)

        if not sys_prompt:
            raise ValueError(f"Improperly formatted prompt file. {path}")

        prompt = cls(
            name=front["name"],
            description=front["description"],
            system_prompt=sys_prompt,
            field_prompts=fields,
        )
        return prompt

    def field_classes(self) -> dict[str, Any]:
        """Return field classes indexed by column/header name."""
        return {f.name: f.field_class() for f in self.field_prompts.values()}

    def column_names(self) -> list[str]:
        """Get all column names."""
        return [c for f in self.field_prompts.values() for c in f.columns]

    def build_field_prompts(self) -> str:
        formatted = [
            f"{i}. {p}"
            for f in self.field_prompts.values()
            for i, p in enumerate(f.prompts, 1)
        ]
        return "\n".join(formatted)

    def build_field_template(self) -> str:
        template = ["Structure all output with the following template."]
        template += [
            f"<< ## {c} ## >>\n{{{c}}}"
            for f in self.field_prompts.values()
            for c in f.columns
        ]
        template.append("<< ## completed ## >>")
        return "\n\n".join(template)

    @staticmethod
    def build_text_prompt(text: str) -> str:
        return "Extract data from this `text` (str):\n" + text
