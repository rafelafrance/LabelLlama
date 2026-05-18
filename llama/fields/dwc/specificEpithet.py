from dataclasses import dataclass, field
from typing import Any

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


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

