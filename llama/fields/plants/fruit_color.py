from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

FRUIT_COLOR: str = compress("""
    Extract the color(s) of the fruits of the specimen.
    Examples: 'red', 'black', 'purple', 'green', 'brown', 'orange',
    'dark blue', 'reddish-brown', 'yellow when ripe'.
    If no fruit color is stated, return the default value.
    """)


@dataclass
class FruitColor(BaseField):
    fruitColor: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.fruitColor = fix_values.hallucinated_str(self.fruitColor, text)
        self.fruitColor = fix_values.remove_trailing_punct(self.fruitColor)
