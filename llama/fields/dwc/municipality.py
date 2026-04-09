from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

MUNICIPALITY: str = compress("""
    Collected from this municipality. This can be a city, town, etc.
    """)


@dataclass
class Municipality(BaseField):
    municipality: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.municipality = fix_values.to_str(self.municipality).title()


DEFAULTS = DotDict({f.name: f.default for f in fields(Municipality)})
