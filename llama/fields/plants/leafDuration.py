from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class LeafDuration(ExtractedField):
    leafDuration: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafDuration = self.hallucinated_str(self.leafDuration, text)
