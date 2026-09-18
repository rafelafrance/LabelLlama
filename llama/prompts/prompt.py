import json
import os
import re
from enum import StrEnum
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar

from llama.prompts.prompt_markdown_parser import PromptMarkdownParser

if TYPE_CHECKING:
    from pathlib import Path

OCR_REQUIRED = ["source", "text"]
FIRST_COLUMNS = ["status", "source", "elapsed", "text"]


class Thinking(StrEnum):
    USE_SERVER = "use server"
    DISABLE_TEMPLATE = "disable template"
    DISABLE_ARG = "disable arg"


class Prompt:
    # -------------- ClassVars ---------------
    text_msg: ClassVar[str] = """Extract data from this `text`:\n\n"""
    # ----------------------------------------

    def __init__(
        self,
        prompt_md: Path,
        model_id: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        thinking: Thinking = Thinking.USE_SERVER,
    ) -> None:
        prompt_parser = PromptMarkdownParser(prompt_md)
        self.name = prompt_parser.name
        self.description = prompt_parser.description
        self.req_fields = prompt_parser.req_fields

        self.columns = [*FIRST_COLUMNS]

        self.json_schema = ""

        self.system_msg = prompt_parser.system_msg

        if prompt_parser.llm_fields:
            self.columns += [f.name for f in prompt_parser.llm_fields]

            self.system_msg += self.build_field_guidance(prompt_parser)
            self.system_msg += dedent("""
                \nStructure the output as JSON using this JSON schema.
                """)

            self.json_schema = self.build_json_schema(prompt_parser)
            self.system_msg += self.json_schema

        self._headers: dict = self.header_template()
        self._payload: dict = self.payload_template(
            model_id, temperature, max_tokens, thinking
        )

    def headers(self) -> dict:
        return self._headers

    def image_payload(self, mime_type: str, base64_image: str) -> dict:
        target_msg = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}",
                    },
                },
            ],
        }
        messages = [*self._payload["messages"]]
        messages[-1] = target_msg
        payload_ = {**self._payload, "messages": messages}
        return payload_

    def text_payload(self, text: str) -> dict:
        target_msg = {"role": "user", "content": self.text_msg + text}
        messages = [*self._payload["messages"]]
        messages[-1] = target_msg
        payload_ = {**self._payload, "messages": messages}
        return payload_

    def header_template(self) -> dict:
        head = {"Content-Type": "application/json"}
        if api_key := os.getenv("LLM_API_KEY"):
            head["Authorization"] = f"Bearer {api_key}"
        return head

    def payload_template(
        self,
        model_id: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        thinking: Thinking = Thinking.USE_SERVER,
    ) -> dict:
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": self.system_msg},
                {"role": "replace me"},
            ],
        }
        if self.json_schema:
            payload["response_format"] = self.json_schema

        if temperature is not None:
            payload["temperature"] = temperature

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        match thinking:
            case Thinking.DISABLE_TEMPLATE:
                payload["chat_template_kwargs"] = {"enable_thinking": False}
            case Thinking.DISABLE_ARG:
                payload["enable_thinking"] = False
            case Thinking.USE_SERVER:
                pass
            case _:
                raise TypeError

        return payload

    def build_field_guidance(self, prompt_parser: PromptMarkdownParser) -> str:
        guidance = ["\n\n# Field Guidance\n"]
        for fld in prompt_parser.llm_fields:
            desc = " ".join(fld.field_class.description.split())
            guidance.append(f"- `{fld.name}`: {desc}")
        guidance.append("")
        return "\n".join(guidance)

    def build_json_schema(self, prompt_parser: PromptMarkdownParser) -> str:
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
            obj["json_schema"]["schema"]["required"] = prompt_parser.req_fields

        schema = "\n" + json.dumps(obj, indent=2)

        # Compress vertically so I can read it
        schema = re.sub(r'\s+("type": "string")\s+', r" \1 ", schema)
        match = re.search(r'"required": \[[^\]]+\]', schema)
        if match:
            replace = " ".join(match.group(0).split())
            schema = re.sub(r'"required": \[[^\]]+\]', replace, schema)

        return schema

    def parse_model_json(self, content: str) -> dict:
        content = content.replace("```json", "").replace("```", "")
        extracted = json.loads(content)
        if not isinstance(extracted, dict):
            raise TypeError("Model response JSON must be an object")
        return extracted
