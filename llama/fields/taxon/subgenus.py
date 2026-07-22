from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Subgenus(ExtractedField):
    subgenus: str = ""

    def __post_init__(self, text: str) -> None:
        self.subgenus = fix_parses.hallucinated_str(self.subgenus, text)
