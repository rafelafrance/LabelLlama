from dataclasses import dataclass
from typing import Any, ClassVar

from llama.llm_fields.llm_field import LlmField
from llama.vocab.taxon import GENUS_TO_FAMILY


@dataclass
class Family(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the taxonomic family name applied to the specimen. Use only the family
        explicitly present in the text; do not infer family from genus.
        """
    scoring_method: ClassVar[str] = "CUST"
    # --------------

    family: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.family = self.to_str(self.family).title()

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        genus = str(record.get("scientificName") or "").split()
        genus = genus[0] if len(genus) > 0 else ""

        # OK if expect is empty and the sci name genus is in the family
        if not expect and GENUS_TO_FAMILY.get(genus) == actual:
            return 1.0

        return LlmField.score(expect, actual, record)  # Default to edit distance
