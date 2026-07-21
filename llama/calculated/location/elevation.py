from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField
from llama.pylib import fix_parses
from llama.vocab import about, units


@dataclass
class Pair:
    value: float
    units: str


@dataclass
class Elevation(CalculatedField):
    elevation: float | str = ""
    minimumElevationInMeters: float | str = ""
    maximumElevationInMeters: float | str = ""
    elevationUnits: str = ""
    elevationEstimated: bool | str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        elev = fix_parses.to_str(record.get("verbatimElevation"))

        units_ = [u.lower() for u in units.get_length_units(elev)]

        values = fix_parses.FLOAT.findall(elev)
        values = fix_parses.to_list_of_floats(values)

        # Make sure every value has units
        if len(values) > len(units_):
            units_ = [u for u in units_ for _ in range(2)]

        # Pair up values with units
        pairs = [Pair(v, u) for v, u in zip(values, units_, strict=False)]

        # Remove any pairs that are not for meters, if there are meters in the units
        if any(p.units.startswith("m") for p in pairs):
            pairs = [p for p in pairs if p.units.startswith("m")]

        # If there are no pairs then something went wrong
        if not pairs:
            self.elevation = ""
            self.minimumElevationInMeters = ""
            self.maximumElevationInMeters = ""
            self.elevationUnits = ""
            self.elevationEstimated = ""
            return

        # Now set the output fields based on the pairs or values and units
        pairs = sorted(pairs, key=lambda p: p.value)
        units_ = pairs[0].units
        low = units.to_meters(pairs[0].value, units_)
        high = units.to_meters(pairs[1].value, units_) if len(pairs) > 1 else ""

        self.elevation = pairs[0].value
        self.minimumElevationInMeters = low
        self.maximumElevationInMeters = high
        self.elevationUnits = units_
        self.elevationEstimated = about.is_about(elev)
