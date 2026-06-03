import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class TrsSection(BaseField):
    trsSection: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsSection = fix_values.to_str(self.trsSection)

        # Remove section label
        self.trsSection = re.sub(r"\b(sec[\w.])|s\.?)\b", "", self.trsSection).strip()
