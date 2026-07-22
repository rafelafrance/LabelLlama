from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Suborder(ExtractedField):
    suborder: str = ""

    def __post_init__(self, text: str) -> None:
        self.suborder = fix_parses.hallucinated_str(self.suborder, text)
