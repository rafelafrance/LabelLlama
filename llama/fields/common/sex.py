from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SEX: str = compress("""
    `sex` (str):
    Extract the sex of the individual insect specimen.
    This describes the biological sex of the specimen as recorded on the
    label. It is distinct from life stage (e.g., 'larva', 'pupa', 'nymph')
    and from morphological castes (e.g., 'queen', 'worker', 'soldier')
    in social insects.

    Full terms: 'male', 'female'.

    Abbreviations: 'm', 'M', 'f', 'F', 'mal', 'fem', '♂', '♀', 'm.', 'f.'.

    Combined or paired specimens: '♂♀', '♀♂', 'pair', '2m', '2f', 'mf',
    'fm', 'male & female', 'male and female'.

    Uncertain or undetermined: 'unknown', 'unsexed', 'sex unknown',
    'unsexed specimen'.

    Do not confuse sex with developmental stage (e.g., 'larva', 'pupa',
    'nymph', 'imago', 'adult') or social-insect caste (e.g., 'queen',
    'worker', 'drone').

    If no sex information is stated, return an empty string.
    """)


@dataclass
class Sex(BaseField):
    sex: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.sex = fix_values.hallucinated_str(self.sex, text)

        if self.sex.lower().startswith("m") or self.sex == "♂":
            self.sex = "male"
        elif self.sex.lower().startswith("f") or self.sex == "♀":
            self.sex = "female"
