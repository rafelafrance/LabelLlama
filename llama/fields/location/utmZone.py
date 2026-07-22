import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class UtmZone(ExtractedField):
    utmZone: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmZone = fix_parses.to_str(self.utmZone)
        self.utmZone = re.sub(r"\b(zone|z\.?)\b", "", self.utmZone).strip()
