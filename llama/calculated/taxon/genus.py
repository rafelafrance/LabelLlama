from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class Genus(CalculatedField):
    genus: str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Get the genus from the scientific name if it is missing here."""
        if not self.genus:
            words = record["scientificName"].split()
            self.genus = words[0].capitalize() if len(words) > 0 else ""
