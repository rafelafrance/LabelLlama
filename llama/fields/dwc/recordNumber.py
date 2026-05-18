import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

RECORD_NUMBER: str = compress("""
    `recordNumber` (str):
    Extract the record number, an identifier given to the occurrence at the time it was
    recorded. It often serves as a link between field notes and a occurrence record,
    such as a specimen's collector number.
    Do not confuse this with a catalog number.
    It is a unique identifier for the collection event, not the collector's personal ID.
    It typically appears near the collector's name or event date and may be
    preceded by '#' or 'Nº'.
    Examples: '12345', 'Smith 1234', 'acc. 4567'.
    If no record number is present, return an empty string.
    """)

SOURCE_THRESHOLD = 75.0


@dataclass
class RecordNumber(BaseField):
    recordNumber: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.recordNumber = fix_values.to_str(self.recordNumber)
        self.recordNumber = re.sub(r"(#|Nº)", "", self.recordNumber)

        # Remove the record number label
        words = self.recordNumber.split()
        words = [s for s in words if not s.lower().startswith("no")]
        words = [s for s in words if not s.lower().startswith("num")]
        words = [s for s in words if not s.lower().startswith("rec")]
        self.recordNumber = " ".join(words)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Remove the record number if it is obviously another number."""
        if source := record.get("source"):
            source = Path(source).stem
            if fuzz.partial_ratio(self.recordNumber, source) > SOURCE_THRESHOLD:
                self.recordNumber = ""
