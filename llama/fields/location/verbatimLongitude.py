from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class VerbatimLongitude(BaseField):
    verbatimLongitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimLongitude = fix_values.to_str(self.verbatimLongitude)
