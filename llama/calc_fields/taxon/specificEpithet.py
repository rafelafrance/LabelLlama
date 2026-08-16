from dataclasses import dataclass
from typing import Any

from llama.calc_fields.calc_field import CalcField


@dataclass
class SpecificEpithet(CalcField):
    specificEpithet: str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Get the specific epithet from the scientific name if it is missing here."""
        cleaned_rec = cleaned_rec or {}

        if not self.specificEpithet:
            words = cleaned_rec.get("scientificName", "").split()
            if words:
                self.specificEpithet = words[1].lower() if len(words) > 1 else ""
