from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Suborder(ExtractedField):
    suborder: str = ""

    def __post_init__(self, text: str) -> None:
        self.suborder = self.hallucinated_str(self.suborder, text)
