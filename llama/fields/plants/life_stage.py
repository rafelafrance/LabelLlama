from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LIFE_STAGE: str = compress("""
    What is the plant's life stage?
    "germination", "seedling", "growing", "maturating", "pollinating", "fertilizing",
    "flowering", "fruiting", "seeding", "dormant", "decaying", "vernalization".
    """)


@dataclass
class LifeStage(BaseField):
    life_stage: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.life_stage = fix_values.to_str(self.life_stage)


DEFAULTS = DotDict({f.name: f.default for f in fields(LifeStage)})
