from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LEAF_MARGIN: str = compress("""
    Description of the specimen's leaf margins.
    Examples: "entire", "crenate", "dentate", "serrate".
    """)


@dataclass
class LeafMargin(BaseField):
    leafMargin: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.leafMargin = fix_values.to_str(self.leafMargin)


DEFAULTS = DotDict({f.name: f.default for f in fields(LeafMargin)})
