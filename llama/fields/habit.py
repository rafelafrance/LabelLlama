from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

HABIT: str = compress("""
    What is the specimen habit?
    Examples: "herbaceous", "woody", "decumbent", "erect".
    """)


@dataclass
class Habit(BaseField):
    habit: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.habit = fix_values.to_str(self.habit)
        self.flowerColor = fix_values.remove_trailing_punct(self.habit)


DEFAULTS = DotDict({f.name: f.default for f in fields(Habit)})
