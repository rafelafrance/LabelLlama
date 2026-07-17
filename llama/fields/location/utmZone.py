import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class UtmZone(BaseField):
    utmZone: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmZone = fix_parses.to_str(self.utmZone)
        self.utmZone = re.sub(r"\b(zone|z\.?)\b", "", self.utmZone).strip()
