from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Island(BaseField):
    island: str = ""

    def __post_init__(self, text: str) -> None:
        self.island = fix_parses.hallucinated_str(self.island, text)
