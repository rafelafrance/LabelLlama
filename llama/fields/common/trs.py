import re
from dataclasses import dataclass, field
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.fields.base_field import BOTH, BaseField
from llama.fields.common import trs_quad, trs_range, trs_section, trs_township
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
        desc=trs_township.TRS_TOWNSHIP,
    )
    trsRange: str = OutputField(
        desc=trs_range.TRS_RANGE,
    )
    trsSection: str = OutputField(
        desc=trs_section.TRS_SECTION,
    )
    trsQuad: str = OutputField(
        desc=trs_quad.TRS_QUAD,
    )
