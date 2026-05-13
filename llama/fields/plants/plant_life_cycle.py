from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

PLANT_LIFE_CYCLE: str = compress("""
    `plantLifeCycle` (str):
    Extract the plant's life cycle or duration (how long the plant lives).
    Examples: 'annual', 'biennial', 'perennial', 'fugacious', 'marcescent',
    'monocarpic', 'semelparous', 'iteroparous', 'persistent', 'subpersistent'.
    If no life cycle information is stated, return an empty string.
    """)


@dataclass
class PlantLifeCycle(BaseField):
    plantLifeCycle: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.plantLifeCycle = fix_values.hallucinated_str(self.plantLifeCycle, text)
