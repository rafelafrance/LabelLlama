from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LIFE_STAGE: str = compress("""
    Extract the developmental or phenological stage of the specimen.
    This describes the current growth phase or maturity level of the plant
    at the time of collection. It is distinct from life cycle
    (annual/biennial/perennial) and from flowersPresent/fruitPresent booleans.

    Developmental maturity: 'seedling', 'juvenile', 'immature', 'young',
    'mature', 'adult', 'old', 'senescent', 'established', 'sapling',
    'seed', 'propagule', 'tissue culture', 'ex vitro'.

    Reproductive/phenological state: 'flowering', 'in flower', 'blooming',
    'fruiting', 'in fruit', 'seeding', 'in seed', 'flower and fruit',
    'fl. and fr.', 'flowering and fruiting', 'flowering and seeding'.

    Seasonal/resting state: 'dormant', 'dormancy', 'resting', 'dormant
    with buds', 'dormant with flower buds', 'dormant with fruit'.

    If no life stage information is stated, return an empty string.
    """)


@dataclass
class LifeStage(BaseField):
    lifeStage: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.lifeStage = fix_values.hallucinated_str(self.lifeStage, text)
