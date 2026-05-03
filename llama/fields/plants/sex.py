from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
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
        self.sex = fix_values.hallucinated_str(self.sex, text)
