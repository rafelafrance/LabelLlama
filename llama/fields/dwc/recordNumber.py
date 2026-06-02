import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values

SOURCE_THRESHOLD = 75.0


@dataclass
class RecordNumber(BaseField):
    recordNumber: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.recordNumber = fix_values.to_str(self.recordNumber)
        self.recordNumber = re.sub(r"(#|Nº)", "", self.recordNumber)

        # Remove the label
        self.recordNumber = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*", "", self.recordNumber, flags=re.IGNORECASE
        )

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Remove the record number if it is obviously another number."""
        if source := record.get("source"):
            source = Path(source).stem
            if fuzz.partial_ratio(self.recordNumber, source) > SOURCE_THRESHOLD:
                self.recordNumber = ""
