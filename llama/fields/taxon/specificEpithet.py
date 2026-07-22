from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class SpecificEpithet(ExtractedField):
    specificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.specificEpithet = fix_parses.to_str(self.specificEpithet).lower()
