from dataclasses import dataclass, field, fields
from typing import Any

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField
from llama.vocab.taxon import GENUS_TO_FAMILY

FAMILY: str = compress("""Taxonomic family is typically near the scientific name.""")


@dataclass
class Family(BaseField):
    family: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.family = fix_values.to_str(self.family).title()

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Add a family name using the genus if the family is missing."""
        if not self.family:
            sci_name = fix_values.to_str(record.get("scientificName", ""))
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

        return BaseField.score(expect, actual, record)  # Default to edit distance


DEFAULTS = DotDict({f.name: f.default for f in fields(Family)})
