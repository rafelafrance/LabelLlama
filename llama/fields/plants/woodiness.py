from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Woodiness(BaseField):
    woodiness: str = ""

    def __post_init__(self, text: str) -> None:
        self.woodiness = fix_parses.hallucinated_str(self.woodiness, text)
