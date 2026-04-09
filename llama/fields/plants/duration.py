from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

DURATION: str = compress("""
    What is the noted plant duration?
    Examples: "annual", "biennial", "fugacious", "marcescent", "monocarp", "monocarpic",
    "perennial", "persistent", "semelparous", "subpersistent".
    """)


@dataclass
class Duration(BaseField):
    duration: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.duration = fix_values.to_str(self.duration)


DEFAULTS = DotDict({f.name: f.default for f in fields(Duration)})
