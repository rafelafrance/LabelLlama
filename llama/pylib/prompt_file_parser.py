import re
from dataclasses import dataclass, field
from pathlib import Path

from llama.parser_utils.field_action import FieldAction
from llama.pylib.prompt_util import get_front_yaml

FIELD_PROMPT_DIR = Path("prompts")


# Regexes for getting the sections of a prompt markdown file
SYS_MSG = re.compile(r"^System\s+Message", flags=re.IGNORECASE)
LLM_FIELDS = re.compile(r"^LLM\s+Fields", flags=re.IGNORECASE)
CALC_FIELDS = re.compile(r"^Calculated\s+Fields", flags=re.IGNORECASE)
JSON_SCHEMA = re.compile(r"```json(.*)```", flags=re.DOTALL)


@dataclass
class PromptFileParser:
    name: str = ""
    description: str = ""
    system_msg: str = ""
    json_schema: dict = field(default_factory=dict)
    llm_fields: list[FieldAction] = field(default_factory=list[FieldAction])
    calc_fields: list[FieldAction] = field(default_factory=list[FieldAction])

    @classmethod
    def load(cls, prompt_path: Path) -> PromptFileParser:
        with prompt_path.open() as f:
            text = f.read()

        front = get_front_yaml(text, prompt_path)

        # Split Markdown file into sections
        sections = re.split(r"^(?<!#)#\s", text, flags=re.MULTILINE)

        sys_msg, schema = "", {}
        llm_fields, calc_fields = [], []

        for section in sections:
            section = section.strip()

            # Get system prompt section
            if SYS_MSG.match(section):
                sys_msg = SYS_MSG.sub("", section).strip()
                match = JSON_SCHEMA.search(sys_msg)
                if match:
                    schema = match.group(1).strip()
                sys_msg = sys_msg.replace("```json\n", "").replace("\n```", "")

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

        prompt = cls(
            name=front["name"],
            description=front["description"],
            system_msg=sys_msg,
            json_schema=schema,
            llm_fields=llm_fields,
            calc_fields=calc_fields,
        )
        return prompt
