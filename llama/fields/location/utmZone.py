import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class UtmZone(BaseField):
    utmZone: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.utmZone = fix_values.to_str(self.utmZone)

        # Remove the zone label
        self.utmZone = re.sub(r"\b(zone|z\.?)\b", "", self.utmZone).strip()
