from dataclasses import dataclass, field
from typing import Any

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField
from llama.vocab.taxon import GENUS_TO_FAMILY


@dataclass
class Family(BaseField):
    family: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.family = fix_values.to_str(self.family).title()

    def cross_field_update(self, record: dict[str, Any]) -> None:
        if not self.family:
            genus = record.get("scientificName", "").split()
            genus = genus[0] if len(genus) > 0 else ""
            self.family = GENUS_TO_FAMILY.get(genus, "")
