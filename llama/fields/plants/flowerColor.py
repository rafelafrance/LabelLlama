from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class FlowerColor(ExtractedField):
    flowerColor: str = ""

    def __post_init__(self, text: str) -> None:
        self.flowerColor = self.hallucinated_str(self.flowerColor, text)
        self.flowerColor = self.remove_trailing_punct(self.flowerColor)
