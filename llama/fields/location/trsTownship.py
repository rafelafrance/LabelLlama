import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class TrsTownship(BaseField):
    trsTownship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsTownship = fix_values.to_str(self.trsTownship)
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
        self.trsTownship = self.trsTownship.strip()
