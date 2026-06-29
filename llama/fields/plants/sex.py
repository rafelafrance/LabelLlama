from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Sex(BaseField):
    sex: str = ""

    def __post_init__(self, text: str) -> None:
        self.sex = fix_parses.hallucinated_str(self.sex, text)
