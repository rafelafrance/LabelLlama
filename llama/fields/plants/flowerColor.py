from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.flowerColor = fix_parses.hallucinated_str(self.flowerColor, text)
        self.flowerColor = fix_parses.remove_trailing_punct(self.flowerColor)
