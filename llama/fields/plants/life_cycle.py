from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

DURATION: str = compress("""
    What is the noted plant duration?
    Examples: "annual", "biennial", "fugacious", "marcescent", "monocarp", "monocarpic",
    "perennial", "persistent", "semelparous", "subpersistent", "iteroparity".
    """)


@dataclass
class LifeCycle(BaseField):
    lifeCycle: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = fix_values.hallucinated_str(self.lifeCycle, text)
