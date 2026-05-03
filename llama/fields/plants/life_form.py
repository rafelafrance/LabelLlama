from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

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
