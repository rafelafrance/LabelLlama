import re
from dataclasses import dataclass, field
from typing import Any

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField

MIN_WORDS = 2
SKIP_FIELDS = ("occurrenceRemarks", "associatedTaxa")


@dataclass
class OccurrenceRemarks(BaseField):
    occurrenceRemarks: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.occurrenceRemarks = fix_values.to_str(self.occurrenceRemarks)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """
        Remove values from any other field.

        Also remove ID numbers and do the best we can with labels.
        """
        for key, value in record.items():
            if not self.occurrenceRemarks:
                return

            if key in SKIP_FIELDS:
                continue

            # Remove when another field is contained in the occurrenceRemarks
            pattern = re.escape(str(value))
            self.occurrenceRemarks = re.sub(pattern, "", self.occurrenceRemarks)

            # Remove when the occurrenceRemarks are contained in another field
            pattern = re.escape(self.occurrenceRemarks)
            if re.match(pattern, str(value)):
                self.occurrenceRemarks = ""

        # Remove easy to get ID number labels
        self.occurrenceRemarks = re.sub(r"(#|Nº)", "", self.occurrenceRemarks)

        words = self.occurrenceRemarks.split()

        # Remove common labels
        words = [
            w
            for w in words
            if not re.match(r"(no\.|num|rec|verif|det|coll:)", w, flags=re.IGNORECASE)
        ]

        self.occurrenceRemarks = " ".join(words)
        self.occurrenceRemarks = self.occurrenceRemarks.strip()

        # Remove residual punctuation
        self.occurrenceRemarks = re.sub(r"\s+[.,;:_-]$", "", self.occurrenceRemarks)
        self.occurrenceRemarks = re.sub(r"^[.,;:_-]\s*$", "", self.occurrenceRemarks)

        # Remove ID numbers
        if all(re.fullmatch(r"\w*\d+\w*", w) for w in words):
            self.occurrenceRemarks = ""

        # If we just have a few small words then kill it
        if len(words) <= MIN_WORDS and all(re.fullmatch(r".{,2}", w) for w in words):
            self.occurrenceRemarks = ""
