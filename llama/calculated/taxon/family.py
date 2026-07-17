from dataclasses import dataclass
from typing import Any, ClassVar

from llama.calculated.calculated_field import CalculatedField
from llama.vocab.taxon import GENUS_TO_FAMILY


@dataclass
class Family(CalculatedField):
    # --------------
    scoring_method: ClassVar[str] = "CUST"
    # --------------

    family: str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Add a family name using the genus if the family is missing."""
        if not self.family:
            sci_name = record.get("scientificName", "")
            words = sci_name.split()
            genus = words[0] if len(words) > 0 else ""
            self.family = GENUS_TO_FAMILY.get(genus, "")

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        genus = record.get("scientificName", "").split()
        genus = genus[0] if len(genus) > 0 else ""

        # OK if expect is empty and the sci name genus is in the family
        if not expect and GENUS_TO_FAMILY.get(genus) == actual:
            return 1.0

        return CalculatedField.score(expect, actual, record)  # Default to edit distance
