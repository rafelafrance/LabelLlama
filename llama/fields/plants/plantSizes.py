from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class PlantSizes(BaseField):
    plantSizes: list[str] | str = field(default_factory=list, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.plantSizes = fix_values.to_list_of_strs(self.plantSizes)
        self.plantSizes = fix_values.reduce_str_list(self.plantSizes)
