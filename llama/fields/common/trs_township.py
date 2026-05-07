import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

TRS_TOWNSHIP: str = compress("""
    `trsTownship` (str):
    Extract the township portion of the TRS coordinates. It will look like
    'T28N', 'T 32 N', or 'T.43'. The letter 'T' followed by digits and an
    'N' or 'S' compass direction. Return only the value without the 'T' prefix.
    If no township is present, return an empty string.
    """)


@dataclass
class Trs(BaseField):
    trsTownship: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.trsTownship = fix_values.to_str(self.trsTownship)
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
