from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

MUNICIPALITY: str = compress("""
    `municipality` (str):
    Extract the municipality where the specimen was collected. This can be a
    city, town, village, or other populated place.
    Do not include the state/province or country — those have their own fields.
    If no municipality is stated, return an empty string.
    """)


@dataclass
class Municipality(BaseField):
    municipality: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.municipality = fix_values.hallucinated_str(self.municipality, text)
