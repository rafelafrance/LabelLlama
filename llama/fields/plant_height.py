from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

PLANT_HEIGHT: str = compress("""How tall is the specimen.""")


@dataclass
class PlantHeight(BaseField):
    plantHeight: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.plantHeight = fix_values.to_str(self.plantHeight)


DEFAULTS = {f.name: f.default for f in fields(PlantHeight)}
