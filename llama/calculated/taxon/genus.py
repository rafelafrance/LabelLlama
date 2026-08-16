from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class Genus(CalculatedField):
    genus: str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Get the genus from the scientific name if it is missing here."""
        cleaned_rec = cleaned_rec or {}

        if not self.genus:
            words = cleaned_rec.get("scientificName", "").split()
            if words:
                self.genus = words[0].capitalize() if len(words) > 0 else ""
