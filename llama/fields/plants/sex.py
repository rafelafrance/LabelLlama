from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Sex(ExtractedField):
    sex: str = ""

    def __post_init__(self, text: str) -> None:
        self.sex = fix_parses.hallucinated_str(self.sex, text)
