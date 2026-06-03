from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Woodiness(BaseField):
    woodiness: str = ""

    def __post_init__(self, text: str) -> None:
        self.woodiness = fix_values.hallucinated_str(self.woodiness, text)
