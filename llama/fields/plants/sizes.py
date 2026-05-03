from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SIZES: str = compress("""
    Extract dimensions of plant parts other than the overall plant height.
    This is a catch-all for measurements of individual organs or structures
    (e.g., leaf size, flower size, fruit size, stem diameter, root length).
    It is distinct from plantHeight (overall vertical size of the whole plant),
    which belongs in its own field.

    Common measurements: leaf length/width, petal size, corolla diameter,
    sepal length, stamen length, style length, ovary size, fruit diameter,
    capsule length, nut size, seed dimensions, stipule size, petiole length,
    internode length, stem diameter, root/rhizome length, bulb size,
    corm diameter, tuber dimensions, branch length, crown width.

    Each size should be a self-contained measurement with units,
    e.g., 'leaves 5-10 cm', 'corolla 1.5 cm wide', 'fruit 3 mm diam'.
    Preserve the text exactly as written, including ranges and units.
    If no size information is stated, return the default value.
    """)


@dataclass
class Sizes(BaseField):
    sizes: list[str] | str | None = field(default_factory=list, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.sizes = fix_values.to_list_of_strs(self.sizes)
        self.sizes = fix_values.reduce_str_list(self.sizes)
