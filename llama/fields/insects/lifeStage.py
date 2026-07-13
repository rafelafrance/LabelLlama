from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class LifeStage(BaseField):
    lifeStage: str = ""

    def __post_init__(self) -> None:
        self.lifeStage = fix_parses.to_str(self.lifeStage)
