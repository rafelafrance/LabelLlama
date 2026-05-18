from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

VERBATIM_LONGITUDE: str = compress("""
    `verbatimLongitude` (str):
    Extract the verbatim longitude at which the specimen was collected.
    Preserve the value exactly as written — it may be decimal degrees
    (e.g., '-93.5678'), degrees/minutes/seconds (e.g., '93°34'05"W'),
    or a coordinate pair. Longitude must fall between -180.0 and 180.0 degrees.
    Exclude the label itself (e.g., 'long.', 'longitude').
    If no longitude is present, return an empty string.
    """)


@dataclass
class VerbatimLongitude(BaseField):
    verbatimLongitude: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimLongitude = fix_values.to_str(self.verbatimLongitude)
