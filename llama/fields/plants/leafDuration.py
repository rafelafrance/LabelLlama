from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class LeafDuration(BaseField):
    leafDuration: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafDuration = fix_parses.hallucinated_str(self.leafDuration, text)
