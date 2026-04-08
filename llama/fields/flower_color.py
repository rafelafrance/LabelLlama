from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

FLOWER_COLOR: str = compress("""What are the colors of the flowers?""")


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.flowerColor = fix_values.to_str(self.flowerColor)
        self.flowerColor = fix_values.remove_trailing_punct(self.flowerColor)


DEFAULTS = {f.name: f.default for f in fields(FlowerColor)}
