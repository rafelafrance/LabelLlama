from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class PlantHeight(BaseField):
    plantHeight: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.plantHeight = fix_parses.to_str(self.plantHeight)
