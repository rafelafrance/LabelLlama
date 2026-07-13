from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = ""

    def __post_init__(self) -> None:
        self.flowerColor = fix_parses.to_str(self.flowerColor)
        self.flowerColor = fix_parses.remove_trailing_punct(self.flowerColor)
