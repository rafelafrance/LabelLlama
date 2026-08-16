from dataclasses import dataclass
from typing import Any

from llama.calc_fields.calc_field import CalcField


@dataclass
class Genus(CalcField):
    genus: str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Get the genus from the scientific name if it is missing here."""
        cleaned_rec = cleaned_rec or {}

        if not self.genus:
            words = cleaned_rec.get("scientificName", "").split()
            if words:
                self.genus = words[0].capitalize() if len(words) > 0 else ""
