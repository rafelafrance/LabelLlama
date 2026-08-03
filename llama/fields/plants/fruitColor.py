from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class FruitColor(ExtractedField):
    fruitColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.fruitColor = self.hallucinated_str(self.fruitColor, text)
        self.fruitColor = self.remove_trailing_punct(self.fruitColor)
