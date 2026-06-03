from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.flowerColor = fix_values.hallucinated_str(self.flowerColor, text)
        self.flowerColor = fix_values.remove_trailing_punct(self.flowerColor)
