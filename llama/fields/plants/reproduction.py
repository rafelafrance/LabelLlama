from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Reproduction(BaseField):
    reproduction: str = ""

    def __post_init__(self) -> None:
        self.reproduction = fix_parses.to_str(self.reproduction)
