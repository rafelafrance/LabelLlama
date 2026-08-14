import re
from dataclasses import dataclass, field
from pathlib import Path

from llama.parser_utils.calc_field import CalcField
from llama.parser_utils.field_prompt import FieldPrompt
from llama.pylib.prompt_util import get_front_yaml

FIELD_PROMPT_DIR = Path("prompts")


# Regexes for getting the sections of a prompt markdown file
SYS_MSG = re.compile(r"^System\s+Message", flags=re.IGNORECASE)
LLM_FIELDS = re.compile(r"^LLM\s+Fields", flags=re.IGNORECASE)
CALC_FIELDS = re.compile(r"^Calculated\s+Fields", flags=re.IGNORECASE)


@dataclass
class PromptFileParser:
    name: str = ""
    description: str = ""
    system_msg: str = ""
    fields: dict[str, FieldPrompt] = field(default_factory=dict[str, FieldPrompt])
    calc_fields: dict[str, CalcField] = field(default_factory=dict[str, CalcField])

    @classmethod
    def load(cls, prompt_path: Path) -> PromptFileParser:
        with prompt_path.open() as f:
            text = f.read()

        front = get_front_yaml(text, prompt_path)

        # Split Markdown file into sections
        sections = re.split(r"^(?<!#)#\s", text, flags=re.MULTILINE)

        sys_msg = ""
        fields, calc_fields = {}, {}

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
                    fields[lnk] = FieldPrompt.load(lnk)

            # Get calculated fields
            elif CALC_FIELDS.match(section):
                section = CALC_FIELDS.sub("", section).strip()
                links = re.findall(r"\([\w/.]+\)", section)
                for lnk in links:
                    lnk = lnk.removeprefix("(").removesuffix(")")
                    calc_fields[lnk] = CalcField.load(lnk)

        prompt = cls(
            name=front["name"],
            description=front["description"],
            system_msg=sys_msg,
            fields=fields,
            calc_fields=calc_fields,
        )
        return prompt
