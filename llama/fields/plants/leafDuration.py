from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class LeafDuration(ExtractedField):
    leafDuration: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafDuration = fix_parses.hallucinated_str(self.leafDuration, text)
