import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class TrsQuad(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the named map quadrangle associated with the locality or TRS data. Do
        not confuse quadrangle names with township, range, or section values.
        """
    # --------------

    trsQuad: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsQuad = self.to_str(self.trsQuad)
        self.trsQuad = re.sub(r"\b(quad\w*|q\.?)\b", "", self.trsQuad).strip()
