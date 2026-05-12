from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ELEVATION_ESTIMATED: str = compress("""
    `elevationEstimated` (bool):
    Determine whether the elevation an estimate?
    Look for words like 'approx.', 'est.', 'ca.', 'about', 'approximately', '~', or '?'
    near the elevation value.
    If no information about elevation estimation is stated, return an empty string.
    """)


@dataclass
class ElevationEstimated(BaseField):
    elevationEstimated: bool | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.elevationEstimated = fix_values.to_truthy(self.elevationEstimated)
