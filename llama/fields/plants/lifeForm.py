from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class LifeForm(ExtractedField):
    lifeForm: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeForm = fix_parses.hallucinated_str(self.lifeForm, text)
