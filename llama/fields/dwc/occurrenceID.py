import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, HIDE, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

OCCURRENCE_ID: str = compress("""
    `occurrenceID` (str):
    Extract the occurrence ID.
	An identifier for the occurrence (as opposed to a particular digital record of the
    occurrence).
    preceded by '#' or 'Nº'.
    If no occurrence ID is present, return an empty string.
    """)


@dataclass
class OccurrenceID(BaseField):
    occurrenceID: str = field(default="", metadata=BOTH | HIDE)

    def __post_init__(self, text: str) -> None:
        del text

        self.occurrenceID = fix_values.to_str(self.occurrenceID)
        self.occurrenceID = re.sub(r"(#|Nº)", "", self.occurrenceID)

        # Remove the record number label
        words = self.occurrenceID.split()
        words = [s for s in words if not s.lower().startswith("no")]
        words = [s for s in words if not s.lower().startswith("num")]
        words = [s for s in words if not s.lower().startswith("rec")]
        self.occurrenceID = " ".join(words)
