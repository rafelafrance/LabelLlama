from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Subgenus(BaseField):
    subgenus: str = ""

    def __post_init__(self, text: str) -> None:
        self.subgenus = fix_values.hallucinated_str(self.subgenus, text)
