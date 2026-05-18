import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

TRS_RANGE: str = compress("""
    `trsRange` (str):
    Extract the range portion of the TRS coordinates. It will look like
    'R23E', 'R 1 W', 'R.11W'. The letter 'R' followed by digits and an
    'E' or 'W' compass direction. Return only the value without the 'R' prefix.
    If no range is present, return an empty string.
    """)


@dataclass
class Trs(BaseField):
    trsRange: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.trsRange = fix_values.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)
