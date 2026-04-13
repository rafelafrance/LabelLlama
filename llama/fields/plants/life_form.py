from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LIFE_FORM: str = compress("""
    How does the plant make its living? Is it parasitic or an epiphyte? Does it grow
    on rocks or other plants? Does it like salty environments?
    Examples: "ecotone", "ectogenesis", "ectoparasite", "epigeal", "epigean", "epigeic",
    "epigeous", "epilithic", "epiphloedal", "epiphloedic", "epiphyllous", "epiphyte",
    "epiphytic", "euryhaline", "eurythermous", "geophytic", "lithophytic", "parasitic",
    """)


@dataclass
class LifeForm(BaseField):
    lifeForm: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeForm = fix_values.hallucinated_str(self.lifeForm, text)


DEFAULTS = DotDict({f.name: f.default for f in fields(LifeForm)})
