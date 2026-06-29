from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class LifeStage(BaseField):
    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_parses.hallucinated_str(self.lifeStage, text)
