import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses

SOURCE_THRESHOLD = 75.0


@dataclass
class RecordNumber(BaseField):
    recordNumber: str = ""

    def __post_init__(self) -> None:
        self.recordNumber = fix_parses.to_str(self.recordNumber)
        self.recordNumber = re.sub(r"(#|Nº)", "", self.recordNumber)

        # Remove the label
        self.recordNumber = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*", "", self.recordNumber, flags=re.IGNORECASE
        ).strip()

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Remove the record number if it is obviously another number."""
        if source := record.get("source"):
            source = Path(source).stem
            if fuzz.partial_ratio(self.recordNumber, source) > SOURCE_THRESHOLD:
                self.recordNumber = ""
