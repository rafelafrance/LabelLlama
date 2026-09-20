import re
from pathlib import Path

import yaml

from llama.prompts.field_action import FieldAction

FIELD_PROMPT_DIR = Path("prompts")


# Regexes for getting the sections of a prompt markdown file
SYS_MSG = re.compile(r"^System\s+Message", flags=re.IGNORECASE)
LLM_FIELDS = re.compile(r"^LLM\s+Fields", flags=re.IGNORECASE)
CALC_FIELDS = re.compile(r"^Calculated\s+Fields", flags=re.IGNORECASE)
REQ_FIELDS = re.compile(r"^Required\s+Fields", flags=re.IGNORECASE)


def get_front_yaml(text: str, path: Path) -> dict:
    top = re.search("^---$.*?^---$", text, flags=re.MULTILINE | re.DOTALL)
    if not top:
        raise ValueError(f"Improperly formatted prompt file. {path}")

    top = top.group(0).replace("---", "")
    front = yaml.safe_load(top)
    return front


class PromptMarkdownParser:
    def __init__(self, prompt_md: Path) -> None:
        with prompt_md.open() as f:
            text = f.read()

        front = get_front_yaml(text, prompt_md)
        self.name: str = front["name"]
        self.description: str = front["description"]
        self.system_msg: str = ""
        self.llm_fields: list[FieldAction] = []
        self.calc_fields: list[FieldAction] = []
        self.req_fields: list[str] = []

        # Split Markdown file into sections
        sections = re.split(r"^(?<!#)#\s", text, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()

            # Get system prompt section
            if SYS_MSG.match(section):
                self.system_msg = SYS_MSG.sub("", section).strip()

            # Get output LLM fields list section
            elif LLM_FIELDS.match(section):
                section = LLM_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/.]+\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    self.llm_fields.append(FieldAction(lnk))

            # Get calculated fields
            elif CALC_FIELDS.match(section):
                section = CALC_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/.]+\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    self.calc_fields.append(FieldAction(lnk))

            # Get required fields
            elif REQ_FIELDS.match(section):
                section = REQ_FIELDS.sub("", section).strip()
                self.req_fields = [
                    name
                    for ln in section.splitlines()
                    if (name := re.sub(r"^\s*\-\s*", "", ln).strip())
                ]

        # Required fields must be in the LLM fields
        llm_fields = {f.name for f in self.llm_fields}
        if req := set(self.req_fields) - llm_fields:
            raise ValueError(
                f"There are required fields not in prompt's LLM fields: {req}"
            )
