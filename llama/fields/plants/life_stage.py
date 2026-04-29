from dataclasses import dataclass, field

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LIFE_STAGE: str = compress("""
    What is the plant's life stage?
    "germination", "seedling", "growing", "maturating", "pollinating", "fertilizing",
    "flowering", "fruiting", "seeding", "dormant", "decaying", "vernalization".
    """)


@dataclass
class LifeStage(BaseField):
    lifeStage: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_values.hallucinated_str(self.lifeStage, text)
