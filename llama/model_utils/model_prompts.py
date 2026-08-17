from dataclasses import dataclass, field
from textwrap import dedent, indent
from typing import TYPE_CHECKING, ClassVar

from llama.model_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class OcrPrompt:
    name: str = ""
    description: str = ""
    system_msg: str = ""

    @classmethod
    def load(cls, prompt_path: Path) -> OcrPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            system_msg=prompt_parser.system_msg,
        )
        return prompt


@dataclass
class ParserPrompt:
    # -------------- ClassVars ---------------
    text_msg: ClassVar[str] = """Extract data from this `text`:\n\n"""
    # ----------------------------------------

    name: str = ""
    description: str = ""
    system_msg: str = ""
    json_schema: str = ""
    column_names: list[str] = field(default_factory=list[str])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            system_msg=prompt_parser.system_msg,
            column_names=[f.name for f in prompt_parser.llm_fields],
        )
        prompt.json_schema = prompt._build_json_schema(prompt_parser)
        prompt.system_msg += dedent("""
            \nStructure the output as JSON using this JSON schema.
            """)
        prompt.system_msg += prompt.json_schema
        return prompt

    def _build_json_schema(self, prompt_parser: PromptFileParser) -> str:
        prefix = dedent(f"""
            {{
              "type": "json_schema",
              "json_schema": {{
                "name": "{self.name}",
                "schema": {{
                  "type": "object",
                  "properties": {{""")
        suffix = dedent("""
                  }
                }
              }
            }
            """)
        llm_fields = []
        for fld in prompt_parser.llm_fields:
            desc = " ".join(fld.field_class.description.split())
            prop = indent(
                dedent(f"""
            "{fld.name}": {{
              "type": "string",
              "description": "{desc}"
            }}"""),
                " " * 8,
            )
            llm_fields.append(prop)
        schema = prefix + ",".join(llm_fields) + suffix
        return schema

    def build_text_msg(self, text: str) -> str:
        return self.text_msg + text
