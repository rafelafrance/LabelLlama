import json
import re
from dataclasses import dataclass, field
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar

from llama.model_utils.ocr_prompt import FIRST_COLUMNS
from llama.model_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class ParserPrompt:
    # -------------- ClassVars ---------------
    text_msg: ClassVar[str] = """Extract data from this `text`:\n\n"""
    # ----------------------------------------

    name: str = ""
    description: str = ""
    system_msg: str = ""
    json_schema: str = ""
    columns: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, prompt_path: Path) -> ParserPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            system_msg=prompt_parser.system_msg,
            columns=FIRST_COLUMNS + [f.name for f in prompt_parser.llm_fields],
        )
        prompt.json_schema = prompt._build_json_schema(prompt_parser)
        prompt.system_msg += prompt._build_field_guidance(prompt_parser)
        prompt.system_msg += dedent("""
            \nStructure the output as JSON using this JSON schema.
            """)
        prompt.system_msg += prompt.json_schema
        return prompt

    def _build_field_guidance(self, prompt_parser: PromptFileParser) -> str:
        guidance = ["\n\n# Field Guidance\n"]
        for fld in prompt_parser.llm_fields:
            desc = " ".join(fld.field_class.description.split())
            guidance.append(f"- `{fld.name}`: {desc}")
        guidance.append("")
        return "\n".join(guidance)

    def _build_json_schema(self, prompt_parser: PromptFileParser) -> str:
        obj = {
            "type": "json_schema",
            "json_schema": {
                "name": self.name,
                "schema": {"type": "object", "properties": {}},
            },
        }
        obj["json_schema"]["schema"]["properties"] = {
            fld.name: {"type": "string"} for fld in prompt_parser.llm_fields
        }
        if prompt_parser.req_fields:
            obj["json_schema"]["required"] = prompt_parser.req_fields

        schema = "\n" + json.dumps(obj, indent=2)

        # Compress vertically so I can read it
        schema = re.sub(r'\s+("type": "string")\s+', r" \1 ", schema)
        match = re.search(r'"required": \[[^\]]+\]', schema)
        if match:
            replace = " ".join(match.group(0).split())
            schema = re.sub(r'"required": \[[^\]]+\]', replace, schema)

        return schema

    def build_text_msg(self, text: str) -> str:
        return self.text_msg + text
