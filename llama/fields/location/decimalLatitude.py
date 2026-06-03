from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class DecimalLatitude(BaseField):
    decimalLatitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        lat = fix_values.to_float(self.decimalLatitude)
        self.decimalLatitude = lat if lat is not None else ""
