from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

VERBATIM_LONGITUDE: str = compress("""
    The specimen was collected at this longitude.
    Longitude must fall in the range of -180.0 degrees to 180.0 degrees.
    """)


@dataclass
class Longitude(BaseField):
    verbatimLongitude: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimLongitude = fix_values.to_str(self.verbatimLongitude)
