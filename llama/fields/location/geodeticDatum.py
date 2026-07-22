from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class GeodeticDatum(ExtractedField):
    geodeticDatum: str = ""

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = fix_parses.hallucinated_str(self.geodeticDatum, text)
