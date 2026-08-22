from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Trs(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the complete Township-Range-Section location string exactly as written,
        including township, range, section, meridian, and aliquot parts when present.
        """
    # --------------

    trs: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trs = self.to_str(self.trs)
