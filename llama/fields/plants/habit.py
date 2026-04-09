from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

HABIT: str = compress("""
    What is the plant's habit or general shape?
    Examples: "acaulescent", "acid plant", "actinomorphic", "arborescent", "ascending",
    "assurgent", "branching", "caducous", "caespitose", "caulescent", "cespitose",
    "climbing", "climbing plant", "creeping", "decumbent", "deflexed",
    "determinate growth", "dimorphic", "ecad", "ecotone", "ectogenesis",
    "ectoparasite", "epigeal", "epigean", "epigeic", "epigeous", "epilithic",
    "epiphloedal", "epiphloedic", "epiphyllous", "epiphyte", "epiphytic",
    "equinoctial", "erect", "escape", "eupotamous", "euryhaline", "eurythermous",
    "exclusive species", "exotic", "exsiccatus", "free-standing", "frutescent",
    "fruticose", "humifuse", "indeterminate growth", "lax", "liana", "parasitic",
    "precocious", "procumbent", "prostrate", "repent", "semi-erect", "shrubby",
    "subacaulescent", "subcaulescent", "subshrubby", "suffrutescent", "treelet",
    "treelets", "upright", "vine", "vines", "virgate", "tree", "bush".
    """)


@dataclass
class Habit(BaseField):
    habit: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.habit = fix_values.to_str(self.habit)


DEFAULTS = DotDict({f.name: f.default for f in fields(Habit)})
