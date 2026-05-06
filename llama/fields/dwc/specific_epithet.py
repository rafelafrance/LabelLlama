from dataclasses import dataclass, field
from typing import Any

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SPECIFIC_EPITHET: str = compress("""
    `specificEpithet` (str):
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
        self.specificEpithet = fix_values.to_str(self.specificEpithet).lower()

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Get the specific epithet from the scientific name if it is missing here."""
        if not self.specificEpithet:
            words = record["specificEpithet"].split()
            self.specificEpithet = words[1].lower() if len(words) > 1 else ""

