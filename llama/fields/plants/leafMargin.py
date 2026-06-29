from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class LeafMargin(BaseField):
    leafMargin: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafMargin = fix_parses.hallucinated_str(self.leafMargin, text)
