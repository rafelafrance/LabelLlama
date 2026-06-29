from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class IslandGroup(BaseField):
    islandGroup: str = ""

    def __post_init__(self, text: str) -> None:
        self.islandGroup = fix_parses.hallucinated_str(self.islandGroup, text)
