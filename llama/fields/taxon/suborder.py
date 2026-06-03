from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Suborder(BaseField):
    suborder: str = ""

    def __post_init__(self, text: str) -> None:
        self.suborder = fix_values.hallucinated_str(self.suborder, text)
