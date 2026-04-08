from dataclasses import dataclass, field, fields
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

UTM: str = compress("""
    Universal Transverse Mercator (UTM).
    Examples "33T 500000 4649776", "Z12 N7874900 E768500",
    "11S 316745.14 3542301.90", "10 3756206N, 0769161E",
    "11S - 0484145E, 3741382N", "10S, 709280 E, 3913480 N",
    "Zone 11S; 3845372N 0729522E", "4057.5 N, 368.1 E".
    """)
UTM_NORTHING: str = compress("""
    The northing portion of the UTM.
    It is a number (possibly negative, or a decimal) followed by an "N".
    It will look like: "3845372N", "4057.6 N", "3968400 N", "N 4253279", "4N".
    Northing is never negative so dashes are separators and not minus signs.
    """)
UTM_EASTING: str = compress("""
    The easting portion of the UTM.
    It is a number (possibly negative, or a decimal) followed by an "E".
    Examples look like "E 642700", "509257E", "0484145E", "546936",
    "368.2 E", "6E".
    Easting is never negative so dashes are separators and not minus signs.
    """)
UTM_ZONE: str = compress("""
    The zone portion of the UTM.
    It will look like: "10S", "11", "8N", "Zone 11S;", "NH", "16P", "LJ".
    """)


@dataclass
class Utm(BaseField):
    predictor: ClassVar[Any] = None

    utm: str = field(default="", metadata=BOTH)
    utmNorthing: str = field(default="", metadata=BOTH)
    utmEasting: str = field(default="", metadata=BOTH)
    utmZone: str = field(default="", metadata=BOTH)

    @classmethod
    def setup_postprocessing(cls) -> None:
        cls.predictor = dspy.Predict(UtmSig)

    def __post_init__(self, text: str) -> None:
        del text

        # Set up the utm so it is valid input for further processing
        self.utm = fix_values.to_str(self.utm)
        self.clean_subfields()

    def run_field_model(self) -> None:
        # Only run the model if an input field is empty
        # Input for this class is actually an output from the LM model class
        if not self.utm or (self.utmNorthing and self.utmEasting and self.utmZone):
            return

        predicted = self.predictor(utm=self.utm)

        # Only fill fields without a previous value, i.e. default to previous LLM
        self.utmNorthing = self.utmNorthing or predicted.get("utmNorthing", "")
        self.utmEasting = self.utmEasting or predicted.get("utmEasting", "")
        self.utmZone = self.utmZone or predicted.get("utmZone", "")

        self.clean_subfields()

    def clean_subfields(self) -> None:
        # Make sure a language model didn't do something silly
        self.utmNorthing = fix_values.to_str(self.utmNorthing)
        self.utmEasting = fix_values.to_str(self.utmEasting)
        self.utmZone = fix_values.to_str(self.utmZone)

        # Remove the E or N for the easting or northing field
        self.utmNorthing = self.utmNorthing.lower().replace("n", "")
        self.utmEasting = self.utmEasting.lower().replace("e", "")

        # Remove the zone label
        words = self.utmZone.split()
        words = [w for w in words if not w.lower().startswith("zone")]
        words = [w for w in words if w.lower() not in ("z", "z.")]
        self.utmZone = " ".join(words)


DEFAULTS = {f.name: f.default for f in fields(Utm)}


@dataclass
class UtmSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    utm = InputField()

    utmNorthing: str = OutputField(
        default="",
        desc=UTM_NORTHING,
    )
    utmEasting: str = OutputField(
        default="",
        desc=UTM_EASTING,
    )
    utmZone: str = OutputField(
        default="",
        desc=UTM_ZONE,
    )
