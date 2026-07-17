from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

from llama.calculated.calculated_field import CalculatedField

SOURCE_THRESHOLD = 75.0


@dataclass
class RecordNumber(CalculatedField):
    recordNumber: str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Remove the record number if it is obviously another number."""
        if source := record.get("source"):
            source = Path(source).stem
            if fuzz.partial_ratio(self.recordNumber, source) > SOURCE_THRESHOLD:
                self.recordNumber = ""
