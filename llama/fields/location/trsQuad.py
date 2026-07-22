import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class TrsQuad(ExtractedField):
    trsQuad: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsQuad = fix_parses.to_str(self.trsQuad)
        self.trsQuad = re.sub(r"\b(quad\w*|q\.?)\b", "", self.trsQuad).strip()
