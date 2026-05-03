import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, HIDE, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

COLLECTOR_NUMBER: str = compress("""
    Extract the collector number (also called access number) assigned to this
    specimen by the collector. It is a unique identifier for the collection event,
    not the collector's personal ID.
    It typically appears near the collector's name or event date and may be
    preceded by '#' or 'Nº'.
    Examples: '12345', 'Smith 1234', 'acc. 4567'.
    If no collector number is present, return the default value.
    """)


@dataclass
class CollectorNumber(BaseField):
    collectorNumber: str = field(default="", metadata=BOTH | HIDE)
    recordNumber: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.collectorNumber = fix_values.to_str(self.collectorNumber)
        self.collectorNumber = re.sub(r"(#|Nº)", "", self.collectorNumber)

        # Remove the record number label
        words = self.collectorNumber.split()
        words = [s for s in words if not s.lower().startswith("no")]
        words = [s for s in words if not s.lower().startswith("num")]
        words = [s for s in words if not s.lower().startswith("rec")]
        self.collectorNumber = " ".join(words)
        self.recordNumber = self.collectorNumber
