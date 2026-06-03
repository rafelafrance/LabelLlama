import re
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values

MIN_WORDS = 2
SKIP_FIELDS = ("occurrenceRemarks", "associatedTaxa")


@dataclass
class OccurrenceRemarks(BaseField):
    occurrenceRemarks: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.occurrenceRemarks = fix_values.to_str(self.occurrenceRemarks)

        # Remove easy to get ID number labels
        self.occurrenceRemarks = re.sub(r"(#|Nº)", "", self.occurrenceRemarks)

        words = self.occurrenceRemarks.split()

        # Remove ID numbers
        if all(re.fullmatch(r"\w*\d+\w*", w) for w in words):
            self.occurrenceRemarks = ""
        else:
            self.occurrenceRemarks = " ".join(words)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
