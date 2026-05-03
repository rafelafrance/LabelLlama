from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

HABIT: str = compress("""
    What is the plant's habit or general shape?
    Examples: "acaulescent", "actinomorphic", "arborescent", "ascending",
    "assurgent", "branching", "caespitose", "caulescent", "cespitose",
    "climbing", "climbing plant", "creeping", "decumbent", "deflexed",
    "determinate growth", "dimorphic", "ecad" "erect", "free-standing", "frutescent",
    "fruticose", "humifuse", "indeterminate growth", "lax", "liana",
    "procumbent", "prostrate", "repent", "semi-erect", "shrubby",
    "subacaulescent", "subcaulescent", "subshrubby", "suffrutescent", "treelet",
    "treelets", "upright", "vine", "vines", "virgate", "tree", "bush".
    """)


@dataclass
class Habit(BaseField):
    habit: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.habit = fix_values.hallucinated_str(self.habit, text)
