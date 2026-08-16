from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from llama.pylib.prompt_file_parser import PromptFileParser

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
    column_names: list[str] = field(default_factory=list[str])

    @classmethod
    def load(cls, prompt_path: Path) -> ParserPrompt:
        prompt_parser = PromptFileParser.load(prompt_path)
        prompt = cls(
            name=prompt_parser.name,
            description=prompt_parser.description,
            system_msg=prompt_parser.system_msg,
            json_schema=prompt_parser.json_schema,
            column_names=[f.name for f in prompt_parser.llm_fields],
        )
        return prompt

    def build_text_msg(self, text: str) -> str:
        return self.text_msg + text
