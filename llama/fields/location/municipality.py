from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class Municipality(BaseField):
    municipality: str = ""

    def __post_init__(self, text: str) -> None:
        self.municipality = fix_values.hallucinated_str(self.municipality, text)
