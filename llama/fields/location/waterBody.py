from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class WaterBody(BaseField):
    waterBody: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.waterBody = fix_values.hallucinated_str(self.waterBody, text)
