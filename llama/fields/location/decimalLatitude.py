from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class DecimalLatitude(BaseField):
    decimalLatitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        lat = fix_parses.to_float(self.decimalLatitude)
        self.decimalLatitude = lat if lat is not None else ""
