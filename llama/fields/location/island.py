from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class Island(BaseField):
    island: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.island = fix_values.hallucinated_str(self.island, text)
