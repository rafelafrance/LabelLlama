from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class IslandGroup(BaseField):
    islandGroup: str = ""

    def __post_init__(self, text: str) -> None:
        self.islandGroup = fix_values.hallucinated_str(self.islandGroup, text)
