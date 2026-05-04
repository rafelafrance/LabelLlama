from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

PLANT_HEIGHT: str = compress("""
    `plantHeight` (str):
    Extract the height of the specimen or the plant as a whole.
    This is a dimension describing vertical size, typically given as a number
    with units (e.g., '15 cm', '1.2 m', '3 ft', '2-5 m').
    It is distinct from other plant part sizes (flower size, leaf size, etc.),
    which belong in the sizes field.

    Look for height indicators like 'ht.', 'height', 'tall', 'long', 'high',
    'reaching', or bare numeric ranges with metric/imperial units.
    Preserve the text exactly as written, including ranges and units.
    Common forms: '10 cm', '0.5-2 m', '15-30 cm tall', 'up to 3 m', 'ca. 50 cm'.

    If no height information is stated, return an empty string.
    """)


@dataclass
class PlantHeight(BaseField):
    plantHeight: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.plantHeight = fix_values.to_str(self.plantHeight)
