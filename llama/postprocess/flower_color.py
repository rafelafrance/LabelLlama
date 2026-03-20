import re
from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class FlowerColor(BaseField):
    flowerColor: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.flowerColor = fix_values.to_str(self.flowerColor)
        self.flowerColor = re.sub(r"[.,;:]$", "", self.flowerColor)
