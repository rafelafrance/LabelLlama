from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

TRS_SECTION: str = compress("""
    `trsSection` (str):
    Extract the section portion of the TRS coordinates. This may include
    quadrant subdivisions (e.g., 'NW 1/4', 'SE ¼') and the section number.
    Examples: '1/4 S10', 'se1/4 ne1/4 sec 12', 'SE ¼ Section 17',
    'NW¼ of sec. 8', 'section 18'. Return only the section value,
    not the 'sec' or 'S' label.
    If no section is present, return an empty string.
    """)


@dataclass
class Trs(BaseField):
    trsSection: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.trsSection = fix_values.to_str(self.trsSection)

        # Remove section label
        words = self.trsSection.split()
        words = [w for w in words if not w.lower().startswith("sec")]
        words = [w for w in words if w.lower() not in ("s", "s.")]
        self.trsSection = " ".join(words)
