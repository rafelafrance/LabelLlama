from dataclasses import dataclass, field

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class PlantSizes(BaseField):
    plantSizes: list[str] | str = field(default_factory=list)

    def __post_init__(self, text: str) -> None:
        del text
        self.plantSizes = fix_parses.to_list_of_strs(self.plantSizes)
        self.plantSizes = fix_parses.reduce_str_list(self.plantSizes)
