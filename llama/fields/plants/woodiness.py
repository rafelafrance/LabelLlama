from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

WOODINESS: str = compress("""
    Is the plant woody or herbaceous?
    Examples: "herbaceous", "herb", "woody", "subherbaceous".
    """)


@dataclass
class Woodiness(BaseField):
    woodiness: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.woodiness = fix_values.hallucinated_str(self.woodiness, text)
