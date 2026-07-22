from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Municipality(ExtractedField):
    municipality: str = ""

    def __post_init__(self, text: str) -> None:
        self.municipality = fix_parses.hallucinated_str(self.municipality, text)
