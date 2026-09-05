import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from llama.prompts.field_action import FieldAction

# Absolute so it works regardless of the current working directory.
FIELD_PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"


# The only headings that start a section of a prompt markdown file. Any other
# '# ' line (e.g. a heading inside the system message body) is left alone.
SECTION_NAMES = (
    "System Message",
    "LLM Fields",
    "Calculated Fields",
    "Required Fields",
)

# Regexes for getting the sections of a prompt markdown file. The split is
# zero-width, so each section keeps its heading line as its first line.
SYS_MSG = re.compile(r"^#\s*System\s+Message", flags=re.IGNORECASE)
LLM_FIELDS = re.compile(r"^#\s*LLM\s+Fields", flags=re.IGNORECASE)
CALC_FIELDS = re.compile(r"^#\s*Calculated\s+Fields", flags=re.IGNORECASE)
REQ_FIELDS = re.compile(r"^#\s*Required\s+Fields", flags=re.IGNORECASE)
JSON_SCHEMA = re.compile(r"```json(.*)```", flags=re.DOTALL)
SECTION_SPLIT = re.compile(
    r"^(?=#\s+(?:" + "|".join(re.escape(n) for n in SECTION_NAMES) + r")\s*$)",
    flags=re.MULTILINE,
)
# A field link is a markdown link, [label](module path). Bare parentheses in
# the prose (e.g. "(v2)") are not links.
FIELD_LINK = re.compile(r"\[[^\]]+\]\(([\w/.]+)\)")


def get_front_yaml(text: str, path: Path) -> dict:
    # Non-greedy: the front matter ends at the NEXT '---' line, not the last
    # one in the file (a later horizontal rule would swallow the document).
    top = re.search("^---$.*?^---$", text, flags=re.MULTILINE | re.DOTALL)
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
        sections = SECTION_SPLIT.split(text)

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
                llm_fields = [
                    FieldAction.load(lnk) for lnk in FIELD_LINK.findall(section)
                ]

            # Get calculated fields
            elif CALC_FIELDS.match(section):
                section = CALC_FIELDS.sub("", section).strip()
                calc_fields = [
                    FieldAction.load(lnk) for lnk in FIELD_LINK.findall(section)
                ]

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
