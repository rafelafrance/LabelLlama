from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class SpecificEpithet(CalculatedField):
    specificEpithet: str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Get the specific epithet from the scientific name if it is missing here."""
        if not self.specificEpithet:
            words = record["specificEpithet"].split()
            self.specificEpithet = words[1].lower() if len(words) > 1 else ""
