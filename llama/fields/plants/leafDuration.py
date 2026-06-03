from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class LeafDuration(BaseField):
    leafDuration: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafDuration = fix_values.hallucinated_str(self.leafDuration, text)
