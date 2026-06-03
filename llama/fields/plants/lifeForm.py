from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class LifeForm(BaseField):
    lifeForm: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeForm = fix_values.hallucinated_str(self.lifeForm, text)
