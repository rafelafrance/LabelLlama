from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.vocab import units as dim_units

ELEVATION_UNITS: str = compress("""
    `elevationUnits` (list[str]):
    Extract the unit(s) for each elevation value (e.g., 'm', 'ft', 'meters', 'feet').
    If multiple values are given, provide a matching unit for each.
    Common units are meters ('m') and feet ('ft').
    If no elevation units are present, return an empty list.
    """)


@dataclass
class ElevationUnits(BaseField):
    elevationUnits: list[str] | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.elevationUnits = fix_values.to_list_of_strs(self.elevationUnits)
        if not self.elevationUnits:
            self.elevationUnits = ""
            return

        self.elevationUnits = [dim_units.normalize(u) for u in self.elevationUnits]

        has_meters = any(u == dim_units.METERS for u in self.elevationUnits)

        if self.elevationUnits and has_meters:
            self.elevationUnits = dim_units.METERS
        elif self.elevationUnits:
            self.elevationUnits = self.elevationUnits[0]

        if isinstance(self.elevationUnits, str):
            self.elevationUnits = fix_values.to_str(self.elevationUnits)
            self.elevationUnits = fix_values.clean_str_ends(self.elevationUnits)
