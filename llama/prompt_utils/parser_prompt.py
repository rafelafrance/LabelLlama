import json
import re
from dataclasses import dataclass, field
from textwrap import dedent
from typing import Any, ClassVar

from llama.prompt_utils.base_prompt import BasePrompt
from llama.prompt_utils.ocr_prompt import FIRST_COLUMNS
from llama.prompt_utils.prompt_file_parser import PromptFileParser


@dataclass
class ParserPrompt(BasePrompt):
    # -------------- ClassVars ---------------
    text_msg: ClassVar[str] = """Extract data from this `text`:\n\n"""
    # ----------------------------------------

    json_schema: str = ""
    columns: list[str] = field(default_factory=list)

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        prompt_parser = PromptFileParser.load(kwargs["prompt"])
        self.name = prompt_parser.name
        self.description = prompt_parser.description

        self.columns = (FIRST_COLUMNS + [f.name for f in prompt_parser.llm_fields],)
        self.json_schema = self._build_json_schema(prompt_parser)

        self.system_msg = prompt_parser.system_msg
        self.system_msg += self._build_field_guidance(prompt_parser)
        self.system_msg += dedent("""
            \nStructure the output as JSON using this JSON schema.
            """)
        self.system_msg += self.json_schema

        self.base_headers = self._headers()
        self.base_payload = self._base_payload(**kwargs)

    def _build_field_guidance(self, prompt_parser: PromptFileParser) -> str:
        guidance = ["\n\n# Field Guidance\n"]
        for fld in prompt_parser.llm_fields:
            desc = " ".join(fld.field_class.description.split())
            guidance.append(f"- `{fld.name}`: {desc}")
        guidance.append("")
        return "\n".join(guidance)

    def _base_payload(self, **kwargs: dict[str, Any]) -> dict:
        payload = {
            "model": kwargs["model_id"],
            "messages": [
                {"role": "system", "content": kwargs["system_msg"]},
                {"role": "replace me"},
            ],
            "response_format": self.json_schema,
        }
        self._payload_args(**kwargs)
        return payload

    def payload(self, text: str) -> dict:
        target_msg = {"role": "user", "content": self.build_text_msg(text)}
        payload_ = self.base_payload
        payload_["messages"][-1] = target_msg
        return payload_

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
