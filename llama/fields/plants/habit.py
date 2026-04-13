from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

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


DEFAULTS = DotDict({f.name: f.default for f in fields(Habit)})
