from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class IslandGroup(BaseField):
    islandGroup: str = ""

    def __post_init__(self) -> None:
        self.islandGroup = fix_parses.to_str(self.islandGroup)
