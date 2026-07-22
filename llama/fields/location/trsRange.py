import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class TrsRange(ExtractedField):
    trsRange: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsRange = fix_parses.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)
