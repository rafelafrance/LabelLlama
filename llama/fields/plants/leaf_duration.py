from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LEAF_DURATION: str = compress("""
    What is the leaf duration?
    Examples: "deciduous", "evergreen", "semi-deciduous", "semi-evergreen".
    """)


@dataclass
class LeafDuration(BaseField):
    leafDuration: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.leafDuration = fix_values.hallucinated_str(self.leafDuration, text)
        del text

        self.leafDuration = fix_values.to_str(self.leafDuration)


DEFAULTS = DotDict({f.name: f.default for f in fields(LeafDuration)})
