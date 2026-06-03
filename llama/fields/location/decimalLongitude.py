from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class DecimalLongitude(BaseField):
    decimalLongitude: float | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.decimalLongitude = fix_values.to_float(self.decimalLongitude) or ""
