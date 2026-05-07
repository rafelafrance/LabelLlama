from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ELEVATION_UNITS: str = compress("""
    `elevationUnits` (list[str]):
    Extract the unit(s) for each elevation value (e.g., 'm', 'ft', 'meters', 'feet').
    If multiple values are given, provide a matching unit for each.
    Common units are meters ('m') and feet ('ft').
    If no elevation units are present, return an empty list.
    """)


@dataclass
class Elevation(BaseField):
    elevationUnits: list[str] | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.elevationUnits = fix_values.to_list_of_strs(self.elevationUnits)
