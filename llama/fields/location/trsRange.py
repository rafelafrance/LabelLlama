import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class TrsRange(BaseField):
    trsRange: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsRange = fix_parses.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)
