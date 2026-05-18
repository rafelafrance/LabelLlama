from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LIFE_STAGE: str = compress("""
    `lifeStage` (str):
    Extract the developmental or phenological stage of the specimen.
    This describes the current developmental phase or maturity level of the insect
    at the time of collection.

    Examples of insect life stages: 'egg', 'larva', 'pupa', 'adult', 'imago', 'nymph'.

    If no life stage information is stated, return an empty string.
    """)


@dataclass
class LifeStage(BaseField):
    lifeStage: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_values.hallucinated_str(self.lifeStage, text)
