from dataclasses import dataclass, field
from typing import Any, ClassVar

import dspy
from dspy import InputField, OutputField, Signature

from llama.fields.base_field import BOTH, IN, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.vocab import units

VERBATIM_ELEVATION: str = compress("""
    `verbatimElevation` (str):
    Extract the verbatim elevation or altitude at which the specimen was collected.
    This may include the numeric value, units, and any labels (e.g., 'elev.', 'alt.',
    'altitude'). Preserve the text exactly as written.
    If no elevation information is present, return an empty string.
    """)
ELEVATION_VALUES: str = compress("""
    `elevationValues` (list[float]):
    Extract the numeric elevation value(s). A single value indicates a point
    elevation; two values indicate an elevation range (min and max).
    The same elevation may be reported in different units — include all numeric values.
    Return only the numbers, not the units.
    If no elevation values are present, return an empty list.
    """)
ELEVATION_UNITS: str = compress("""
    `elevationUnits` (list[str]):
    Extract the unit(s) for each elevation value (e.g., 'm', 'ft', 'meters', 'feet').
    If multiple values are given, provide a matching unit for each.
    Common units are meters ('m') and feet ('ft').
    If no elevation units are present, return an empty list.
    """)
ELEVATION_ESTIMATED: str = compress("""
    `elevationEstimated` (bool):
    Determine whether the elevation an estimate?
    Look for words like 'approx.', 'est.', 'ca.', 'about', 'approximately', '~', or '?'
    near the elevation value.
    If no information about elevation estimation is stated, return an empty string.
    """)


@dataclass
class Elevation(BaseField):
    parse_model: ClassVar[Any] = None

    verbatimElevation: str = field(default="", metadata=BOTH)
    elevationValues: list[float] = field(default_factory=list, metadata=IN)
    elevation: float | str | None = field(default=None, metadata=BOTH)
    maxElevation: float | str | None = field(default=None, metadata=BOTH)
    elevationUnits: list[str] | str | None = field(default=None, metadata=BOTH)
    elevationEstimated: bool | str | None = field(default="", metadata=BOTH)

    @classmethod
    def setup_postprocessing(cls) -> None:
        cls.parse_model = dspy.Predict(ElevationSig)

    def __post_init__(self, text: str) -> None:
        del text

        # Set up the verbatimElevation so it is valid input for further processing
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)
        self.clean_subfields()

    def parse_field(self) -> None:
        # Only run the model if an input field is empty
        # Input for this class is actually an output from the LM model class
        if not self.verbatimElevation or (self.elevationValues and self.elevationUnits):
            return

        predicted = self.parse_model(verbatimElevation=self.verbatimElevation)

        # Only fill fields without a previous value, i.e. default to previous LLM
        self.elevationValues = self.elevationValues or predicted.get(
            "elevationValues", ""
        )
        self.elevationUnits = self.elevationUnits or predicted.get("elevationUnits", "")
        self.elevationEstimated = self.elevationEstimated or ""

        self.clean_subfields()

    def clean_subfields(self) -> None:
        # Make sure the language model didn't do something silly
        self.elevationValues = fix_values.to_list_of_floats(self.elevationValues)
        self.elevationUnits = fix_values.to_list_of_strs(self.elevationUnits)
        self.elevationEstimated = fix_values.to_bool(self.elevationEstimated)

        # Format boolean as None or True
        self.elevationEstimated = self.elevationEstimated or ""

        # Remove the label from verbatimElevation
        words = self.verbatimElevation.split()
        words = [w for w in words if not w.lower().startswith("el")]
        words = [w for w in words if not w.lower().startswith("alt")]
        self.verbatimElevation = " ".join(words)

        # Make sure every value has units
        if len(self.elevationValues) > len(self.elevationUnits):
            self.elevationUnits = [u for u in self.elevationUnits for _ in range(2)]

        # Pair up values and units
        pairs = list(zip(self.elevationValues, self.elevationUnits, strict=False))

        # Remove any pairs that are not for meters, if there actually are meters
        if any(p[1].lower().startswith("m") for p in pairs):
            pairs = [(v, u) for v, u in pairs if u[0].lower().startswith("m")]

        # If there are no pairs then something went wrong
        if not pairs:
            self.elevation = ""
            self.maxElevation = ""
            self.elevationUnits = ""
            self.elevationEstimated = ""
            return

        # Now set the output fields based on the pairs or values and units
        self.elevation = pairs[0][0]
        self.maxElevation = pairs[1][0] if len(pairs) > 1 else ""
        self.elevationUnits = units.elevation(pairs[0][1])


class ElevationSig(Signature):
    """
    Analyze the text and extract this elevation information.

    If the data field is not found in the text return an empty list.
    Do not hallucinate.
    """

    verbatimElevation = InputField()

    elevationValues: list[float] = OutputField(
        desc=ELEVATION_VALUES,
    )
    elevationUnits: list[str] = OutputField(
        desc=ELEVATION_UNITS,
    )
    elevationEstimated: bool = OutputField(
        desc=ELEVATION_ESTIMATED,
    )
