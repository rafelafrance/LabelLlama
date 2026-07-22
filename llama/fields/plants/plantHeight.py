from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class PlantHeight(ExtractedField):
    plantHeight: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.plantHeight = fix_parses.to_str(self.plantHeight)
