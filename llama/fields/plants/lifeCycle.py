from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

PLANT_LIFE_CYCLE: str = compress("""
    `lifeCycle` (str):
    Extract the plant's life cycle or duration (how long the plant lives).
    Examples: 'annual', 'biennial', 'perennial', 'fugacious', 'marcescent',
    'monocarpic', 'semelparous', 'iteroparous', 'persistent', 'subpersistent'.
    If no life cycle information is stated, return an empty string.
    """)


@dataclass
class LifeCycle(BaseField):
    lifeCycle: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = fix_values.hallucinated_str(self.lifeCycle, text)
