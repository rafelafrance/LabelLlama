import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class TrsSection(BaseField):
    trsSection: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsSection = fix_parses.to_str(self.trsSection)
        self.trsSection = re.sub(r"\b(sec[\w.]|s\.?)\b", "", self.trsSection).strip()
