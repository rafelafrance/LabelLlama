from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

FRUIT_COLOR: str = compress("""What are the colors of the fruits?""")


@dataclass
class FruitColor(BaseField):
    fruitColor: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.fruitColor = fix_values.to_str(self.fruitColor)
        self.fruitColor = fix_values.remove_trailing_punct(self.fruitColor)


DEFAULTS = {f.name: f.default for f in fields(FruitColor)}
