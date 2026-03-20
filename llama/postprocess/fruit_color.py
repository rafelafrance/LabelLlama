import re
from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class FruitColor(BaseField):
    fruitColor: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.fruitColor = fix_values.to_str(self.fruitColor)
        self.fruitColor = re.sub(r"[.,;:]$", "", self.fruitColor)
