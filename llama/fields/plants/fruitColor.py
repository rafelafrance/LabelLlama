from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class FruitColor(BaseField):
    fruitColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.fruitColor = fix_values.hallucinated_str(self.fruitColor, text)
        self.fruitColor = fix_values.remove_trailing_punct(self.fruitColor)
