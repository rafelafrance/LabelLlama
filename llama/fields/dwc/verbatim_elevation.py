from dataclasses import dataclass, field
from typing import Any, ClassVar

from llama.fields.base_field import BOTH, IN, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

VERBATIM_ELEVATION: str = compress("""
    `verbatimElevation` (str):
    Extract the verbatim elevation or altitude at which the specimen was collected.
    This may include the numeric value, units, and any labels (e.g., 'elev.', 'alt.',
    'altitude'). Preserve the text exactly as written.
    If no elevation information is present, return an empty string.
    """)

@dataclass
class VerbatimElevation(BaseField):
    parse_model: ClassVar[Any] = None

    verbatimElevation: str = field(default="", metadata=BOTH)
    elevationValues: list[float] = field(default_factory=list, metadata=IN)
    elevation: float | str = field(default="", metadata=BOTH)
    maxElevation: float | str = field(default="", metadata=BOTH)
    elevationUnits: list[str] | str = field(default="", metadata=BOTH)
    elevationEstimated: bool | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        # Set up the verbatimElevation so it is valid input for further processing
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)
        # self.clean_subfields()

    # def clean_subfields(self) -> None:
    #     # Make sure the language model didn't do something silly
    #     self.elevationValues = fix_values.to_list_of_floats(self.elevationValues)
    #     self.elevationUnits = fix_values.to_list_of_strs(self.elevationUnits)
    #     self.elevationEstimated = fix_values.to_bool(self.elevationEstimated)
    #
    #     # Format boolean as None or True
    #     self.elevationEstimated = self.elevationEstimated or ""
    #
    #     # Remove the label from verbatimElevation
    #     words = self.verbatimElevation.split()
    #     words = [w for w in words if not w.lower().startswith("el")]
    #     words = [w for w in words if not w.lower().startswith("alt")]
    #     self.verbatimElevation = " ".join(words)
    #
    #     # Make sure every value has units
    #     if len(self.elevationValues) > len(self.elevationUnits):
    #         self.elevationUnits = [u for u in self.elevationUnits for _ in range(2)]
    #
    #     # Pair up values and units
    #     pairs = list(zip(self.elevationValues, self.elevationUnits, strict=False))
    #
    #     # Remove any pairs that are not for meters, if there actually are meters
    #     if any(p[1].lower().startswith("m") for p in pairs):
    #         pairs = [(v, u) for v, u in pairs if u[0].lower().startswith("m")]
    #
    #     # If there are no pairs then something went wrong
    #     if not pairs:
    #         self.elevation = ""
    #         self.maxElevation = ""
    #         self.elevationUnits = ""
    #         self.elevationEstimated = ""
    #         return
    #
    #     # Now set the output fields based on the pairs or values and units
    #     self.elevation = pairs[0][0]
    #     self.maxElevation = pairs[1][0] if len(pairs) > 1 else ""
    #     self.elevationUnits = units.elevation(pairs[0][1])
