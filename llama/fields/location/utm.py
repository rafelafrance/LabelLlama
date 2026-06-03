from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Utm(BaseField):
    utm: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utm = fix_values.to_str(self.utm)
