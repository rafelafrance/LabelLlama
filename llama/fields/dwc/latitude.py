from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

VERBATIM_LATITUDE: str = compress("""
    `verbatimLatitude` (str):
    Extract the verbatim latitude at which the specimen was collected.
    Preserve the value exactly as written — it may be decimal degrees
    (e.g., '45.1234'), degrees/minutes/seconds (e.g., '45°12'34"N'),
    or a coordinate pair. Latitude must fall between -90.0 and 90.0 degrees.
    Exclude the label itself (e.g., 'lat.', 'latitude').
    If no latitude is present, return an empty string.
    """)


@dataclass
class Latitude(BaseField):
    verbatimLatitude: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimLatitude = fix_values.to_str(self.verbatimLatitude)
