from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class PlantSize(BaseField):
    plantSize: list[str] = field(default_factory=list, metadata=BOTH)

    def __post_init__(self) -> None:
        self.plantSize = fix_values.to_list_of_strs(self.plantSize)
