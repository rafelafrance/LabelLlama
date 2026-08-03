from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class LifeForm(ExtractedField):
    lifeForm: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeForm = self.hallucinated_str(self.lifeForm, text)
