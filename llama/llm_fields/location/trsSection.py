import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class TrsSection(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the section portion of a Township-Range-Section location, including
        aliquot parts such as NE1/4 when they are part of the section description.
        """
    # --------------

    trsSection: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsSection = self.to_str(self.trsSection)
        self.trsSection = re.sub(r"\b(sec[\w.]|s\.?)\b", "", self.trsSection).strip()
