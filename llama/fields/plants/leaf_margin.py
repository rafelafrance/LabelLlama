from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LEAF_MARGIN: str = compress("""
    Extract the description of the specimen's leaf margins (edge shape).
    Examples: 'entire', 'crenate', 'dentate', 'serrate', 'lobed', 'toothed',
    'undulate', 'sinuate', 'ciliate', 'scalloped'.
    If no leaf margin information is stated, return an empty string.
    """)


@dataclass
class LeafMargin(BaseField):
    leafMargin: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.leafMargin = fix_values.hallucinated_str(self.leafMargin, text)
