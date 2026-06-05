import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class Utm(BaseField):
    utm: str = ""
    utmNorthing: str = ""
    utmEasting: str = ""
    utmZone: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utm = fix_values.to_str(self.utm)

        self.utmNorthing = fix_values.to_str(self.utmNorthing)
        self.utmNorthing = self.utmNorthing.lower().replace("n", "")
        self.utmNorthing = "" if self.utmNorthing in EMPTY_NE else self.utmNorthing

        self.utmEasting = fix_values.to_str(self.utmEasting)
        self.utmEasting = self.utmEasting.lower().replace("e", "")
        self.utmEasting = "" if self.utmEasting in EMPTY_NE else self.utmEasting

        self.utmZone = fix_values.to_str(self.utmZone)
        self.utmZone = re.sub(r"\b(zone|z\.?)\b", "", self.utmZone).strip()
