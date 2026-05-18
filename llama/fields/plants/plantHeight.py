from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class PlantHeight(BaseField):
    plantHeight: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.plantHeight = fix_values.to_str(self.plantHeight)
