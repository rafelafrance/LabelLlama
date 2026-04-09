from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

GEODETIC_DATUM: str = compress("""
    What geodetic datum is the latitude, longitude, TRS, or UTM using.
    Examples "NAD27", "NAD83", "WGS84".
    """)


@dataclass
class GeodeticDatum(BaseField):
    geodeticDatum: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = fix_values.hallucinated_str(self.geodeticDatum, text)


DEFAULTS = DotDict({f.name: f.default for f in fields(GeodeticDatum)})
