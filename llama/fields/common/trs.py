import re
from dataclasses import dataclass, field
from typing import Any, ClassVar

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

TRS: str = compress("""
    `trs` (str):
    Extract the Township Range Section (TRS) coordinates from the label.
    TRS is a land survey system used primarily in the United States.
    Preserve the text exactly as written — it may include township, range,
    section, quadrant subdivisions, and a quadrangle (quad) name.
    Examples: 'Bodie Quadrangle; T4N R25E S36', 'T41N R15E NW 1/4 S10',
    'T7S, R1W SE 1/4 sec. 33', 'SW 1/4 sec. 34'.
    If no TRS information is present, return an empty string.
    """)


@dataclass
class Trs(BaseField):
    parse_model: ClassVar[Any] = None

    trs: str = field(default="", metadata=BOTH)
    trsTownship: str = field(default="", metadata=BOTH)
    trsRange: str = field(default="", metadata=BOTH)
    trsSection: str = field(default="", metadata=BOTH)
    trsQuad: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        # Set up the trs so it is valid input for further processing
        self.trs = fix_values.to_str(self.trs)
        self.clean_subfields()

    def clean_subfields(self) -> None:
        # Make sure a language model didn't do something silly
        self.trsTownship = fix_values.to_str(self.trsTownship)
        self.trsRange = fix_values.to_str(self.trsRange)
        self.trsSection = fix_values.to_str(self.trsSection)
        self.trsQuad = fix_values.to_str(self.trsQuad)

        # Remove the T or R from the township and range
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)

        # Remove section label
        words = self.trsSection.split()
        words = [w for w in words if not w.lower().startswith("sec")]
        words = [w for w in words if w.lower() not in ("s", "s.")]
        self.trsSection = " ".join(words)

        # Remove quad label
        words = self.trsQuad.split()
        words = [w for w in words if not w.lower().startswith("quad")]
        words = [w for w in words if w.lower() not in ("q", "q.")]
        self.trsQuad = " ".join(words)
