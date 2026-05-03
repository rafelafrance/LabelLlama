from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LEAF_SHAPE: str = compress("""
    What is the shape of the specimen's leaf?
    Examples: "acute", "caudate", "elliptic", "lobed".
    """)


@dataclass
class LeafShape(BaseField):
    leafShape: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.leafShape = fix_values.hallucinated_str(self.leafShape, text)
