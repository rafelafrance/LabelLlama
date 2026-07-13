from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class DecimalLongitude(BaseField):
    decimalLongitude: float | str = ""

    def __post_init__(self) -> None:
        long = fix_parses.to_float(self.decimalLongitude)
        self.decimalLongitude = long if long is not None else ""
