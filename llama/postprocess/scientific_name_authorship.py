from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class ScientificNameAuthorship(BaseField):
    scientificNameAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        values = fix_values.to_list_of_strs(self.scientificNameAuthorship)
        values = [v.title() for v in values]
        self.scientificNameAuthorship = fix_values.reduce_list(values)
