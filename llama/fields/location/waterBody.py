from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class WaterBody(ExtractedField):
    waterBody: str = ""

    def __post_init__(self, text: str) -> None:
        self.waterBody = fix_parses.hallucinated_str(self.waterBody, text)
