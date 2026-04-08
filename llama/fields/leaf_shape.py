from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LEAF_SHAPE: str = compress("""
    What is the shape of the specimen's leaf?
    Examples: "acute", "caudate", "elliptic", "lobed".
    """)


@dataclass
class LeafShape(BaseField):
    leafShape: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.leafShape = fix_values.to_str(self.leafShape)


DEFAULTS = {f.name: f.default for f in fields(LeafShape)}
