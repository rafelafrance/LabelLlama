from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class LeafMargin(BaseField):
    leafMargin: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.leafMargin = fix_values.to_str(self.leafMargin)
