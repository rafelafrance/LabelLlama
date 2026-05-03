from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

PLANT_REPRODUCTION: str = compress("""
    Extract the plant's breeding system (how sexual organs are distributed
    among flowers and individuals). This describes whether male and female
    reproductive parts occur together or separately at the population level.
    It is distinct from sex (which describes individual flower sex, e.g.,
    'male', 'female', 'bisexual') and from habit (growth shape).

    Breeding system terms: 'monoecious', 'dioecious', 'polygamous',
    'polygamomonoecious', 'polygamodioecious', 'gynodioecious', 'gynodioecy',
    'androdioecious', 'trioecious', 'trimonoecious', 'subdioecious',
    'subandroecious', 'subgynoecious', 'andromonoecious', 'androdioecious',
    'gynomonoecious', 'androecious', 'gynoecious', 'androgynous',
    'androgynomonoecious', 'hermaphroditic', 'hermaphrodite', 'hermaphrodite'.

    Temporal separation: 'dichogamous', 'protandrous', 'protogynous'.

    If no breeding system information is stated, return an empty string.
    """)


@dataclass
class Reproduction(BaseField):
    reproduction: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.reproduction = fix_values.hallucinated_str(self.reproduction, text)
