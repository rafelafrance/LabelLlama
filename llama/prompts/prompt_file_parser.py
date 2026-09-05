import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from llama.prompts.field_action import FieldAction

FIELD_PROMPT_DIR = Path("prompts")


# Regexes for getting the sections of a prompt markdown file
SYS_MSG = re.compile(r"^System\s+Message", flags=re.IGNORECASE)
LLM_FIELDS = re.compile(r"^LLM\s+Fields", flags=re.IGNORECASE)
CALC_FIELDS = re.compile(r"^Calculated\s+Fields", flags=re.IGNORECASE)
REQ_FIELDS = re.compile(r"^Required\s+Fields", flags=re.IGNORECASE)
JSON_SCHEMA = re.compile(r"```json(.*)```", flags=re.DOTALL)


def get_front_yaml(text: str, path: Path) -> dict:
    top = re.search("^---$.*^---$", text, flags=re.MULTILINE | re.DOTALL)
    if not top:
        raise ValueError(f"Improperly formatted prompt file. {path}")

    top = top.group(0).replace("---", "")
    front = yaml.safe_load(top)
    return front


@dataclass
class PromptFileParser:
    name: str = ""
    description: str = ""
    system_msg: str = ""
    llm_fields: list[FieldAction] = field(default_factory=list)
    calc_fields: list[FieldAction] = field(default_factory=list)
    req_fields: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, prompt_path: Path) -> PromptFileParser:
        with prompt_path.open() as f:
            text = f.read()

        front = get_front_yaml(text, prompt_path)

        # Split Markdown file into sections
        sections = re.split(r"^(?<!#)#\s", text, flags=re.MULTILINE)

        sys_msg = ""
        llm_fields, calc_fields, req_fields = [], [], []

        for section in sections:
            section = section.strip()

            # Get system prompt section
            if SYS_MSG.match(section):
                sys_msg = SYS_MSG.sub("", section).strip()

            # Get output LLM fields list section
            elif LLM_FIELDS.match(section):
                section = LLM_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/.]+\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    llm_fields.append(FieldAction.load(lnk))

            # Get calculated fields
            elif CALC_FIELDS.match(section):
                section = CALC_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/.]+\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    calc_fields.append(FieldAction.load(lnk))

            # Get required fields
            elif REQ_FIELDS.match(section):
                section = REQ_FIELDS.sub("", section).strip()
                req_fields = [
                    name
                    for ln in section.splitlines()
                    if (name := re.sub(r"^\s*\-\s*", "", ln).strip())
                ]

        prompt = cls(
            name=front["name"],
            description=front["description"],
            system_msg=sys_msg,
            llm_fields=llm_fields,
            calc_fields=calc_fields,
            req_fields=req_fields,
        )
        return prompt
