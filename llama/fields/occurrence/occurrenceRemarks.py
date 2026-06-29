import re
from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class OccurrenceRemarks(BaseField):
    # --------------
    scoring_method: ClassVar[str] = "FPR"
    # --------------

    occurrenceRemarks: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.occurrenceRemarks = fix_parses.to_str(self.occurrenceRemarks)

        # Remove easy to get ID number labels
        self.occurrenceRemarks = re.sub(r"(#|Nº)", "", self.occurrenceRemarks)

        words = self.occurrenceRemarks.split()

        # Remove ID numbers
        if all(re.fullmatch(r"\w*\d+\w*", w) for w in words):
            self.occurrenceRemarks = ""
        else:
            self.occurrenceRemarks = " ".join(words)

        self.occurrenceRemarks = " ".join(self.occurrenceRemarks.split())

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
