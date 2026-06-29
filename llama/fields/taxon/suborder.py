from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Suborder(BaseField):
    suborder: str = ""

    def __post_init__(self, text: str) -> None:
        self.suborder = fix_parses.hallucinated_str(self.suborder, text)
