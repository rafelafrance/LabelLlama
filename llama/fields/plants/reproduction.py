from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Reproduction(ExtractedField):
    reproduction: str = ""

    def __post_init__(self, text: str) -> None:
        self.reproduction = fix_parses.hallucinated_str(self.reproduction, text)
