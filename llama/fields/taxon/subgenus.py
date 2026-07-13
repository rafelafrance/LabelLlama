from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Subgenus(BaseField):
    subgenus: str = ""

    def __post_init__(self) -> None:
        self.subgenus = fix_parses.to_str(self.subgenus)
