from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Island(ExtractedField):
    island: str = ""

    def __post_init__(self, text: str) -> None:
        self.island = fix_parses.hallucinated_str(self.island, text)
