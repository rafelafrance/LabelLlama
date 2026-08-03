from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class LeafShape(ExtractedField):
    leafShape: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafShape = self.hallucinated_str(self.leafShape, text)
