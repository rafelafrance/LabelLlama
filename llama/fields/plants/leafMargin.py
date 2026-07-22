from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class LeafMargin(ExtractedField):
    leafMargin: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafMargin = fix_parses.hallucinated_str(self.leafMargin, text)
