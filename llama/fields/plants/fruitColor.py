from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class FruitColor(ExtractedField):
    fruitColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.fruitColor = fix_parses.hallucinated_str(self.fruitColor, text)
        self.fruitColor = fix_parses.remove_trailing_punct(self.fruitColor)
