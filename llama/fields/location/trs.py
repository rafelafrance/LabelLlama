import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Trs(BaseField):
    trs: str = ""
    trsTownship: str = ""
    trsRange: str = ""
    trsSection: str = ""
    trsQuad: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trs = fix_values.to_str(self.trs)

        self.trsTownship = fix_values.to_str(self.trsTownship)
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
        self.trsTownship = self.trsTownship.strip()

        self.trsRange = fix_values.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)

        self.trsSection = fix_values.to_str(self.trsSection)
        self.trsSection = re.sub(r"\b(sec[\w.])|s\.?)\b", "", self.trsSection).strip()

        self.trsQuad = fix_values.to_str(self.trsQuad)
        self.trsQuad = re.sub(r"\b(quad\w*|q\.?)\b", "", self.trsQuad).strip()
