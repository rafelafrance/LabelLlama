from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Suborder(BaseField):
    suborder: str = ""

    def __post_init__(self) -> None:
        self.suborder = fix_parses.to_str(self.suborder)
