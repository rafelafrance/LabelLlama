from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

HABIT: str = compress("""
    Extract the plant's habit or general growth form/shape.
    Examples: 'erect', 'ascending', 'prostrate', 'creeping', 'climbing', 'vine',
    'liana', 'shrubby', 'arborescent', 'tree', 'bush', 'caespitose', 'cespitose',
    'decumbent', 'procumbent', 'repent', 'semi-erect', 'upright', 'branching',
    'frutescent', 'suffrutescent', 'acaulescent', 'caulescent', 'lax',
    'actinomorphic', 'fruticose', 'humifuse', 'virgate', 'treelet'.
    If no habit information is stated, return the default value.
    """)


@dataclass
class Habit(BaseField):
    habit: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.habit = fix_values.hallucinated_str(self.habit, text)
