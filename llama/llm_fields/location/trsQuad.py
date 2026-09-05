import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class TrsQuad(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the quadrangle (quad) name associated with the TRS coordinates
        """
    # --------------

    trsQuad: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsQuad = self.to_str(self.trsQuad)
        self.trsQuad = re.sub(r"\b(quad\w*|q\.?)\b", "", self.trsQuad).strip()
