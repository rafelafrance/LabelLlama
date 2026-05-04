from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

FLOWER_COLOR: str = compress("""
    `flowerColor` (str):
    Extract the color(s) of the flowers of the specimen.
    Examples: 'white', 'pink', 'yellow', 'purple', 'blue', 'red', 'cream',
    'greenish-yellow', 'mottled purple and white'.
    If no flower color is stated, return an empty string.
    """)


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.flowerColor = fix_values.hallucinated_str(self.flowerColor, text)
        self.flowerColor = fix_values.remove_trailing_punct(self.flowerColor)
