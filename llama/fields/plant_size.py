from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

PLANT_SIZE: str = compress("""
    Other specimen sizes like plant width, or flower size, etc.
    """)


@dataclass
class PlantSize(BaseField):
    plantSize: list[str] | str | None = field(default_factory=list, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.plantSize = fix_values.to_list_of_strs(self.plantSize)
        self.plantSize = fix_values.reduce_str_list(self.plantSize)


DEFAULTS = {f.name: f.default for f in fields(PlantSize)}
