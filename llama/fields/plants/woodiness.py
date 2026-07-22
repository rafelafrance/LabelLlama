from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class Woodiness(ExtractedField):
    woodiness: str = ""

    def __post_init__(self, text: str) -> None:
        self.woodiness = fix_parses.hallucinated_str(self.woodiness, text)
