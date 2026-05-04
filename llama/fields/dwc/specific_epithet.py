from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SPECIFIC_EPITHET: str = compress("""
    `specificEpithet` str:
    Extract the taxonomic specific epipthet of the specimen
    (e.g., 'exigua', 'lupis', 'domesticus').
    The specific epipthet is typically the second word of the scientific name.
    Return the specific epipthet only — do not include higher or lower ranks.
    If no specific epipthet is stated, return an empty string.
    """)


@dataclass
class SpecificEpithet(BaseField):
    specificEpithet: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.specificEpithet = fix_values.to_str(self.specificEpithet)
