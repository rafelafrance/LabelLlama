from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class Sex(ExtractedField):
    sex: str = ""

    def __post_init__(self, text: str) -> None:
        self.sex = self.hallucinated_str(self.sex, text)
