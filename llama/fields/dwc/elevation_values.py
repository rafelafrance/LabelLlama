from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, IN, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ELEVATION_VALUES: str = compress("""
    `elevationValues` (list[float]):
    Extract the numeric elevation value(s). A single value indicates a point
    elevation; two values indicate an elevation range (min and max).
    The same elevation may be reported in different units — include all numeric values.
    Return only the numbers, not the units.
    If no elevation values are present, return an empty list.
    """)


@dataclass
class Elevation(BaseField):
    elevationValues: list[float] = field(default_factory=list, metadata=IN)
    elevation: float | str = field(default="", metadata=BOTH)
    maxElevation: float | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.elevationValues = fix_values.to_list_of_floats(self.elevationValues)
