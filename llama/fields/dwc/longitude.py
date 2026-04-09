from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
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


DEFAULTS = DotDict({f.name: f.default for f in fields(Longitude)})
