from dataclasses import dataclass
from typing import Any

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class ElevationValues(BaseField):
    elevationValues: list[float] | str = ""
    elevation: float | str = ""
    maxElevation: float | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.elevationValues = fix_values.to_list_of_floats(self.elevationValues)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        units = fix_values.to_list_of_strs(record["elevationUnits"])

        # Make sure every value has units
        if len(self.elevationValues) > len(units):
            units = [u for u in units for _ in range(2)]

        # Pair up values with units
        pairs = list(zip(self.elevationValues, units, strict=False))

        # Remove any pairs that are not for meters, if there actually are meters
        if any(p[1].lower().startswith("m") for p in pairs):
            pairs = [(v, u) for v, u in pairs if u[0].lower().startswith("m")]

        # If there are no pairs then something went wrong
        if not pairs:
            self.elevation = ""
            self.maxElevation = ""
            return

        # Now set the output fields based on the pairs or values and units
        self.elevation = pairs[0][0]
        self.maxElevation = pairs[1][0] if len(pairs) > 1 else ""
