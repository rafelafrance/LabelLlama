from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class LifeStage(BaseField):
    lifeStage: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_values.hallucinated_str(self.lifeStage, text)
