from dataclasses import dataclass
from typing import Any, ClassVar

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses
from llama.vocab.taxon import GENUS_TO_FAMILY


@dataclass
class Family(BaseField):
    # --------------
    scoring_method: ClassVar[str] = "CUST"
    # --------------

    family: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.family = fix_parses.to_str(self.family).title()

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        genus = record.get("scientificName", "").split()
        genus = genus[0] if len(genus) > 0 else ""

        # OK if expect is empty and the sci name genus is in the family
        if not expect and GENUS_TO_FAMILY.get(genus) == actual:
            return 1.0

        return BaseField.score(expect, actual, record)  # Default to edit distance
