from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Subgenus(ExtractedField):
    subgenus: str = ""

    def __post_init__(self, text: str) -> None:
        self.subgenus = self.hallucinated_str(self.subgenus, text)
