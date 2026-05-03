from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

MUNICIPALITY: str = compress("""
    Collected from this municipality. This can be a city, town, etc.
    """)


@dataclass
class Municipality(BaseField):
    municipality: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.municipality = fix_values.hallucinated_str(self.municipality, text)
