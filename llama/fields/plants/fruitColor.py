from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FruitColor(BaseField):
    fruitColor: str = ""

    def __post_init__(self) -> None:
        self.fruitColor = fix_parses.to_str(self.fruitColor)
        self.fruitColor = fix_parses.remove_trailing_punct(self.fruitColor)
