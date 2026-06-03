from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class DecimalLatitude(BaseField):
    decimalLatitude: float | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.decimalLatitude = fix_values.to_float(self.decimalLatitude) or ""
