from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class LeafShape(BaseField):
    leafShape: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafShape = fix_values.hallucinated_str(self.leafShape, text)
