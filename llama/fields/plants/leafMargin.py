from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class LeafMargin(ExtractedField):
    leafMargin: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafMargin = self.hallucinated_str(self.leafMargin, text)
