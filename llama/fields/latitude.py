from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

VERBATIM_LATITUDE: str = compress("""
    The specimen was collected at this latitude.
    Latitude must fall in the range of -90.0 degrees to 90.0 degrees.
    """)


@dataclass
class Latitude(BaseField):
    verbatimLatitude: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimLatitude = fix_values.to_str(self.verbatimLatitude)


DEFAULTS = {f.name: f.default for f in fields(Latitude)}
