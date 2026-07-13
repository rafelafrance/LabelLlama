from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Woodiness(BaseField):
    woodiness: str = ""

    def __post_init__(self) -> None:
        self.woodiness = fix_parses.to_str(self.woodiness)
