from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class LeafShape(BaseField):
    leafShape: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafShape = fix_parses.hallucinated_str(self.leafShape, text)
