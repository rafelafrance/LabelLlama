from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LOCALITY: str = compress("""
        Get the locality from input text string.
        There may be multiple phrases that describe the locality.
        Exclude the TRS, UTM, elevation, and county.
        """)


@dataclass
class Locality(BaseField):
    locality: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.locality = fix_values.to_str(self.locality)


DEFAULTS = {f.name: f.default for f in fields(Locality)}
