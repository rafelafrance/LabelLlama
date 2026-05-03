import re
from dataclasses import dataclass, field
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

TRS: str = compress("""
    Extract the Township Range Section (TRS) coordinates from the label.
    TRS is a land survey system used primarily in the United States.
    Preserve the text exactly as written — it may include township, range,
    section, quadrant subdivisions, and a quadrangle (quad) name.
    Examples: 'Bodie Quadrangle; T4N R25E S36', 'T41N R15E NW 1/4 S10',
    'T7S, R1W SE 1/4 sec. 33', 'SW 1/4 sec. 34'.
    If no TRS information is present, return the default value.
    """)
TRS_TOWNSHIP: str = compress("""
    Extract the township portion of the TRS coordinates. It will look like
    'T28N', 'T 32 N', or 'T.43'. The letter 'T' followed by digits and an
    'N' or 'S' compass direction. Return only the value without the 'T' prefix.
    If no township is present, return the default value.
    """)
TRS_RANGE: str = compress("""
    Extract the range portion of the TRS coordinates. It will look like
    'R23E', 'R 1 W', 'R.11W'. The letter 'R' followed by digits and an
    'E' or 'W' compass direction. Return only the value without the 'R' prefix.
    If no range is present, return the default value.
    """)
TRS_SECTION: str = compress("""
    Extract the section portion of the TRS coordinates. This may include
    quadrant subdivisions (e.g., 'NW 1/4', 'SE ¼') and the section number.
    Examples: '1/4 S10', 'se1/4 ne1/4 sec 12', 'SE ¼ Section 17',
    'NW¼ of sec. 8', 'section 18'. Return only the section value,
    not the 'sec' or 'S' label.
    If no section is present, return the default value.
    """)
TRS_QUAD: str = compress("""
    Extract the quadrangle (quad) name associated with the TRS coordinates.
    The quad may appear before or after the other TRS fields. Examples:
    'USGS Wahtoke 7 1/2 quad', 'Yountville Quad', 'Chicken Hawk Hill quadrangle',
    'Mt. Ingalls quad.'. Return only the quad name, not the 'quad' label.
    If no quadrangle is mentioned, return the default value.
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

    @classmethod
    def setup_postprocessing(cls) -> None:
        cls.parse_model = dspy.Predict(TrsSig)

    def parse_field(self) -> None:
        # Only run the model if an important input field is empty
        # Input for this class is actually an output from the LM moddel class
        if not self.trs or (self.trsTownship and self.trsRange and self.trsSection):
            return

        predicted = self.parse_model(trs=self.trs)

        # Only fill fields without a previous value, i.e. default to previous LLM
        self.trsTownship = self.trsTownship or predicted.get("trsTownship", "")
        self.trsRange = self.trsRange or predicted.get("trsRange", "")
        self.trsSection = self.trsSection or predicted.get("trsSection", "")
        self.trsQuad = self.trsQuad or predicted.get("trsQuad", "")

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


class TrsSig(Signature):
    """
    Analyze the text and extract this TRS (Township Range Section) information.

    If the data field is not found in the text empty fields.
    Do not hallucinate.
    """

    trs = InputField()

    trsTownship: str = OutputField(
        desc=TRS_TOWNSHIP,
    )
    trsRange: str = OutputField(
        desc=TRS_RANGE,
    )
    trsSection: str = OutputField(
        desc=TRS_SECTION,
    )
    trsQuad: str = OutputField(
        desc=TRS_QUAD,
    )
