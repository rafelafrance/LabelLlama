import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class UtmZone(ExtractedField):
    utmZone: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmZone = self.to_str(self.utmZone)
        self.utmZone = re.sub(r"\b(zone|z\.?)\b", "", self.utmZone).strip()
