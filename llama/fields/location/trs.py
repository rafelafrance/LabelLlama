from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Trs(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the full Township-Range-Section (TRS) coordinate string from the label
        """
    # --------------

    trs: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trs = self.to_str(self.trs)
