from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class DecimalLongitude(BaseField):
    decimalLongitude: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        long = fix_values.to_float(self.decimalLongitude)
        self.decimalLongitude = long if long is not None else ""
