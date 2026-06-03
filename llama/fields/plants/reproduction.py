from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Reproduction(BaseField):
    reproduction: str = ""

    def __post_init__(self, text: str) -> None:
        self.reproduction = fix_values.hallucinated_str(self.reproduction, text)
