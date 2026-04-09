import re
from dataclasses import dataclass, field, fields
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

TRS: str = compress("""
    Township Range Section (TRS).
    There may be a quad (quadrangle) associated with the TRS.
    The quad may come before or after the other fields.
    Examples "Bodie Quadrangle; T4N R25E S36", "T41N R15E NW 1/4 S10",
    "T7S, R1W SE 1/4 sec. 33", "SW 1/4 sec. 34.",
    "T23N R14E se1/4 ne1/4 sec 12 Reconnaissance quad",
    "S27, T 48 N , R 7 W Mt. Diablo Mer.",
    "T.43.R.11W., south-east corner section 7".
    """)
TRS_TOWNSHIP: str = compress("""
    The township portion of the TRS. It will look like: "T28N", "T 32 N", or
    "T.43".
    The letter "T" followed by possible punctuation and then a few digits and
    then an "N" or "S" compass direction.
    """)
TRS_RANGE: str = compress("""
    The range portion of the TRS. It will look like: "R23E", "R 1 W", "R.11W".
    The letter "R" followed by possible punctuation then a few digits and
    then an "E" or "W" compass direction.
    """)
TRS_SECTION: str = compress("""
    The section portion of the TRS. Examples look like "1/4 S10",
    '"se1/4 ne1/4  sec 12", "SE ¼ Section 17", "NW¼ of sec. 8", "section 18",
    "S8 (SE¼)", "south-east corner section 7", "w½ne¼ sec 27", "S 12°".
    """)
TRS_QUAD: str = compress("""
    The quad (quadrangle) portion of the TRS. It may be at the beginning or
    end of the TRS.
    Examples look like: "USGS Wahtoke 7 1/2 quad", "Yountville Quad",
    "Chicken Hawk Hill quadrangle", "Mt. Ingalls quad."
    """)


@dataclass
class Trs(BaseField):
    predictor: ClassVar[Any] = None

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
        cls.predictor = dspy.Predict(TrsSig)

    def run_field_model(self) -> None:
        # Only run the model if an important input field is empty
        # Input for this class is actually an output from the LM moddel class
        if not self.trs or (self.trsTownship and self.trsRange and self.trsSection):
            return

        predicted = self.predictor(trs=self.trs)

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


DEFAULTS = DotDict({f.name: f.default for f in fields(Trs)})


class TrsSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    trs = InputField()

    trsTownship: str = OutputField(
        default=DEFAULTS["trsTownship"],
        desc=TRS_TOWNSHIP,
    )
    trsRange: str = OutputField(
        default=DEFAULTS["trsRange"],
        desc=TRS_RANGE,
    )
    trsSection: str = OutputField(
        default=DEFAULTS["trsSection"],
        desc=TRS_SECTION,
    )
    trsQuad: str = OutputField(
        default=DEFAULTS["trsQuad"],
        desc=TRS_QUAD,
    )
