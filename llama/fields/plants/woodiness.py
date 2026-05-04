from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

WOODINESS: str = compress("""
    `woodiness` (str):
    Extract the degree of woodiness of the plant (whether the stem is woody
    or herbaceous). This describes the nature of the above-ground tissue at
    the end of the growing season. It is distinct from habit (growth shape
    or orientation, e.g., 'erect', 'climbing', 'prostrate') and from life
    form (nutritional strategy or substrate, e.g., 'epiphytic', 'parasitic').

    Woody: 'woody', 'tree', 'arborescent', 'shrub', 'frutescent', 'fruticose',
    'shrublet', 'subshrub', 'suffrutescent', 'suffruticose', 'semi-woody',
    'partly woody', 'woody-based', 'woody stem', 'lignified', 'lignified
    at base', 'woody caudex', 'woody rootstock'.

    Herbaceous: 'herbaceous', 'herb', 'subherbaceous', 'soft-stemmed',
    'succulent', 'fleshy', 'herbaceous perennial', 'herbaceous annual'.

    If no woodiness information is stated, return an empty string.
    """)


@dataclass
class Woodiness(BaseField):
    woodiness: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.woodiness = fix_values.hallucinated_str(self.woodiness, text)
