from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class Utm(BaseField):
    utmEasting: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.utmEasting = fix_values.to_str(self.utmEasting)
        self.utmEasting = self.utmEasting.lower().replace("e", "")
        self.utmEasting = "" if self.utmEasting in EMPTY_NE else self.utmEasting
