from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class LeafMargin(BaseField):
    leafMargin: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.leafMargin = fix_values.hallucinated_str(self.leafMargin, text)
