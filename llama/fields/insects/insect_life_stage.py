from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

INSECT_LIFE_STAGE: str = compress("""
    `insectLifeStage` (str):
    Extract the developmental or phenological stage of the specimen.
    This describes the current developmental phase or maturity level of the insect
    at the time of collection.

    Examples of insect life stages: 'egg', 'larva', 'pupa', 'adult', 'imago', 'nymph'.

    If no life stage information is stated, return an empty string.
    """)


@dataclass
class InsectLifeStage(BaseField):
    insectLifeStage: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.insectLifeStage = fix_values.hallucinated_str(self.insectLifeStage, text)
