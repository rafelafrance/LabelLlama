import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class TrsSection(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the section portion of the Township-Range-Section (TRS) coordinates
        """
    # --------------

    trsSection: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsSection = self.to_str(self.trsSection)
        self.trsSection = re.sub(r"\b(sec[\w.]|s\.?)\b", "", self.trsSection).strip()
