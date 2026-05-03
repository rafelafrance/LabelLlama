from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LEAF_DURATION: str = compress("""
    What is the leaf duration?
    Examples: "deciduous", "evergreen", "semi-deciduous", "semi-evergreen".
    """)


@dataclass
class LeafDuration(BaseField):
    leafDuration: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.leafDuration = fix_values.hallucinated_str(self.leafDuration, text)
