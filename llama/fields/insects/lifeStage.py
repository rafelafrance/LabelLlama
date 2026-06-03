from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class LifeStage(BaseField):
    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_values.hallucinated_str(self.lifeStage, text)
