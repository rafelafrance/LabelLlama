from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Sex(BaseField):
    sex: str = ""

    def __post_init__(self) -> None:
        self.sex = fix_parses.to_str(self.sex)
