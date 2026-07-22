from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class VernacularName(ExtractedField):
    vernacularName: str = ""

    def __post_init__(self, text: str) -> None:
        self.vernacularName = fix_parses.hallucinated_str(self.vernacularName, text)
