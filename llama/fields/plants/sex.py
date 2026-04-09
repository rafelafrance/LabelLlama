from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

PLANT_SEX: str = compress("""
    What is the plant's habit?
    Examples: "bisexual", "diclinous", "imperfect", "male", "female", "monoclinous",
    "perfect", "pistillate", "staminate", "synoecious", "unisexual".
    """)


@dataclass
class Sex(BaseField):
    sex: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.sex = fix_values.to_str(self.sex)


DEFAULTS = DotDict({f.name: f.default for f in fields(Sex)})
