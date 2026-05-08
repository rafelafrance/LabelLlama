from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

DECIMAL_LONGITUDE: str = compress("""
    `decimalLongitude` (float):
    Extract the decimal longitude at which the specimen was collected.
    Return only the numeric value as a decimal number.
    Longitude must fall between -180.0 and 180.0 degrees.
        ✅ Include: negative values for Western Hemisphere (e.g., -118.2437),
            positive values for Eastern Hemisphere (e.g., 121.4737, 121.473789).
        ❌ DO NOT include: the label itself (e.g., 'long.', 'longitude', 'Lon:'),
            compass direction letters (e.g., 'E', 'W'), or the paired latitude value.
        ❌ DO NOT include: degrees/minutes/seconds format (e.g., '121°28'25"') —
            that belongs in verbatimLongitude. Only return a plain decimal number.
    Examples: '121.4737', '-118.2437', '0.0', '179.9', '-179.9'.
    If no longitude is present, return an empty string.
    """)


@dataclass
class DecimalLongitude(BaseField):
    decimalLongitude: float | str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.decimalLongitude = fix_values.to_float(self.decimalLongitude) or ""
