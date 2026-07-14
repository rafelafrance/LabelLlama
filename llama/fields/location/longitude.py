from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Longitude(BaseField):
    longitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.longitude = fix_parses.to_str(self.longitude)
