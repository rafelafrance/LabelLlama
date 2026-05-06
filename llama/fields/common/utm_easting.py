from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

UTM_EASTING: str = compress("""
    `utmEasting` (str):
    Extract the easting portion of the UTM coordinates. It is a number
    (possibly decimal) followed by or preceded by an 'E'.
    Examples: 'E 642700', '509257E', '0484145E', '368.2 E'.
    Easting is never negative — dashes are separators, not minus signs.
    Return only the numeric value, not the 'E' label.
    If no easting is present, return an empty string.
    """)


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
