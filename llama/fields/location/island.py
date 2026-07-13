from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Island(BaseField):
    island: str = ""

    def __post_init__(self) -> None:
        self.island = fix_parses.to_str(self.island)
