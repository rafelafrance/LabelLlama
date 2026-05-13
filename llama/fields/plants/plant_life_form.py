from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

PLANT_LIFE_FORM: str = compress("""
    `plantLifeForm` (str):
    Extract the ecological life form (aka niche) of the specimen.
    This describes how the plant obtains nutrients and where it anchors itself.
    It is distinct from habit (growth shape), habitat (physical environment),
    and woodiness (woody vs herbaceous).

    Nutritional strategy: 'parasitic', 'hemiparasitic', 'holoparasitic',
    'saprophytic', 'saprotrophic', 'mycoheterotrophic', 'heterotrophic',
    'myco-heterotrophic', 'chlorophyllous', 'achlorophyllous', 'autotrophic'.

    Substrate association: 'epiphyte', 'epiphytic', 'lithophyte', 'lithophytic',
    'saxicolous', 'saxatile', 'terrestrial', 'geophyte', 'geophytic',
    'rhizomatous', 'bulbous', 'tuberous'.

    Environmental association: 'aquatic', 'semi-aquatic', 'amphibious',
    'hydrophytic', 'halophyte', 'halophytic', 'littoral', 'riparian',
    'xerophytic', 'hygrophytic', 'helophytic'.

    Do not confuse life form with habit (e.g. 'erect', 'climbing', 'prostrate')
    or habitat (e.g. 'forest', 'meadow', 'desert').
    If no life form information is stated, return an empty string.
    """)


@dataclass
class PlantLifeForm(BaseField):
    plantLifeForm: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.plantLifeForm = fix_values.hallucinated_str(self.plantLifeForm, text)
