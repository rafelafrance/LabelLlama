from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

UTM_NORTHING: str = compress("""
    `utmNorthing` (str):
    Extract the northing portion of the UTM coordinates. It is a number
    (possibly decimal) followed by or preceded by an 'N'.
    Examples: '3845372N', '4057.6 N', '3968400 N', 'N 4253279'.
    Northing is never negative — dashes are separators, not minus signs.
    Return only the numeric value, not the 'N' label.
    If no northing is present, return an empty string.
    """)


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
