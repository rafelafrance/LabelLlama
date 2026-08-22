from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from llama.model_utils.prompt_file_parser import PromptFileParser

if TYPE_CHECKING:
    from pathlib import Path

FIRST_COLUMNS = ["status", "source", "elapsed", "text"]


@dataclass
class OcrPrompt:
    # -------------- ClassVars ---------------
    columns: ClassVar[list[str]] = FIRST_COLUMNS
    # ----------------------------------------

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
