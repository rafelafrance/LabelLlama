from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LEAF_DURATION: str = compress("""
    Extract the leaf duration (how long the plant retains its leaves).
    Examples: 'deciduous', 'evergreen', 'semi-deciduous', 'semi-evergreen',
    'marcescent', 'persistent'.
    If no leaf duration information is stated, return the default value.
    """)


@dataclass
class LeafDuration(BaseField):
    leafDuration: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.leafDuration = fix_values.hallucinated_str(self.leafDuration, text)
