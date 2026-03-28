from dataclasses import dataclass
from typing import Any

from llama.score.base_scorer import BaseScorer
from llama.vocab.taxon import GENUS_TO_FAMILY


@dataclass
class FamilyScorer(BaseScorer):
    def cross_field_score(
        self, expect: Any, actual: Any, actual_record: dict[str, Any]
    ) -> float:
        genus = actual_record.get("scientificName", "").split()
        genus = genus[0] if len(genus) > 0 else ""

        # OK if expect is empty and the sci name genus is in the family
        if not expect and GENUS_TO_FAMILY.get(genus) == actual:
            self.cross_field = 1.0
        else:
            self.cross_field = 0.0
        return self.cross_field
