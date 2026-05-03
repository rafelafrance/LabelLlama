from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

FLOWER_COLOR: str = compress("""What are the colors of the flowers?""")


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.flowerColor = fix_values.hallucinated_str(self.flowerColor, text)
        self.flowerColor = fix_values.remove_trailing_punct(self.flowerColor)
