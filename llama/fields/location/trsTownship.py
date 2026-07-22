import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class TrsTownship(ExtractedField):
    trsTownship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsTownship = fix_parses.to_str(self.trsTownship)
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
        self.trsTownship = self.trsTownship.strip()
