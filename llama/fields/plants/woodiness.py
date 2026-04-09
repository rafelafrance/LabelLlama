from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

WOODINESS: str = compress("""
    Is the plant woody or herbaceous?
    Examples: "herbaceous", "herb", "woody", "subherbaceous".
    """)


@dataclass
class Woodiness(BaseField):
    woodiness: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.woodiness = fix_values.to_str(self.woodiness)


DEFAULTS = DotDict({f.name: f.default for f in fields(Woodiness)})
