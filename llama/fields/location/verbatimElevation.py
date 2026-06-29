import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses
from llama.vocab import units as dim_units


@dataclass
class VerbatimElevation(BaseField):
    verbatimElevation: str = ""
    _elevationValues: list[float] | str = ""
    elevationUnits: list[str] | str = ""
    elevationEstimated: bool | str = ""
    elevation: float | str = ""
    maximumElevation: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = fix_parses.to_str(self.verbatimElevation)
        self._elevationValues = fix_parses.to_list_of_floats(self._elevationValues)
        self.elevationUnits = fix_parses.to_list_of_strs(self.elevationUnits)
        self.elevationEstimated = fix_parses.to_truthy(self.elevationEstimated)

        self.clean_verbatim_elevation()
        self.clean_elevation()

    def clean_verbatim_elevation(self) -> None:
        # Remove the label
        self.verbatimElevation = re.sub(
            r"\b(el\w*|alt\w*)\b[:,.;\s]*",
            "",
            self.verbatimElevation,
            flags=re.IGNORECASE,
        ).strip()

    def clean_elevation(self) -> None:
        # Make sure every value has units
        if len(self._elevationValues) > len(self.elevationUnits):
            self.elevationUnits = [u for u in self.elevationUnits for _ in range(2)]

        # Pair up values with units
        pairs = list(zip(self._elevationValues, self.elevationUnits, strict=False))

        # Remove any pairs that are not for meters, if there are meters in the units
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
        self.elevationUnits = dim_units.normalize(pairs[0][1])
