from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class Utm(BaseField):
    utmNorthing: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.utmNorthing = fix_values.to_str(self.utmNorthing)
        self.utmNorthing = self.utmNorthing.lower().replace("n", "")
        self.utmNorthing = "" if self.utmNorthing in EMPTY_NE else self.utmNorthing
