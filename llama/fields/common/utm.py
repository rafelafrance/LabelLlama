from dataclasses import dataclass, field
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.common import utm_easting, utm_northing, utm_zone

UTM: str = compress("""
    `utm` (str):
    Extract the Universal Transverse Mercator (UTM) coordinates from the label.
    UTM coordinates consist of a zone, northing, and easting.
    Preserve the text exactly as written. Examples: '33T 500000 4649776',
    'Z12 N7874900 E768500', '11S 316745.14 3542301.90', 'Zone 11S; 3845372N 0729522E'.
    If no UTM information is present, return an empty string.
    """)


# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class Utm(BaseField):
    parse_model: ClassVar[Any] = None

    utm: str = field(default="", metadata=BOTH)
    utmNorthing: str = field(default="", metadata=BOTH)
    utmEasting: str = field(default="", metadata=BOTH)
    utmZone: str = field(default="", metadata=BOTH)

    @classmethod
    def setup_postprocessing(cls) -> None:
        cls.parse_model = dspy.Predict(UtmSig)

    def __post_init__(self, text: str) -> None:
        del text

        # Set up the utm so it is valid input for further processing
        self.utm = fix_values.to_str(self.utm)
        self.clean_subfields()

    def parse_field(self) -> None:
        # Only run the model if an input field is empty
        # Input for this class is actually an output from the LM model class
        if not self.utm or (self.utmNorthing and self.utmEasting and self.utmZone):
            return

        predicted = self.parse_model(utm=self.utm)

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

        # Remove these odd values from northing or easting
        self.utmNorthing = "" if self.utmNorthing in EMPTY_NE else self.utmNorthing
        self.utmEasting = "" if self.utmEasting in EMPTY_NE else self.utmEasting

        # Remove the zone label
        words = self.utmZone.split()
        words = [w for w in words if not w.lower().startswith("zone")]
        words = [w for w in words if w.lower() not in ("z", "z.")]
        self.utmZone = " ".join(words)


@dataclass
class UtmSig(Signature):
    """
    Analyze the text and extract this UTM (Universal Transverse Mercator)
    coordinate information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    utm = InputField()

    utmNorthing: str = OutputField(
        desc=utm_northing.UTM_NORTHING,
    )
    utmEasting: str = OutputField(
        desc=utm_easting.UTM_EASTING,
    )
    utmZone: str = OutputField(
        desc=utm_zone.UTM_ZONE,
    )
