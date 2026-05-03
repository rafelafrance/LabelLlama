from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

PLANT_SEX: str = compress("""
    Extract the sex of the individual flower(s) or inflorescence on the specimen.
    This describes whether the flowers contain male parts only, female parts only,
    or both. It is distinct from reproduction (breeding system at the
    population level, e.g., 'dioecious', 'monoecious') and from habit
    (growth shape).

    Flower sex terms: 'male', 'female', 'bisexual', 'perfect', 'imperfect',
    'staminate', 'pistillate', 'unisexual', 'monoclinous', 'diclinous',
    'synoecious', 'neuter', 'staminode', 'pistillode', 'androgynous',
    'cleistogamous', 'chasmogamous'.

    If no flower sex information is stated, return the default value.
    """)


@dataclass
class Sex(BaseField):
    sex: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.sex = fix_values.hallucinated_str(self.sex, text)
