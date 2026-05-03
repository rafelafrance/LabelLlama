import re
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

MIN_WORDS = 2
SKIP_FIELDS = ("occurrenceRemarks", "associatedTaxa")

OCCURRENCE_REMARKS: str = compress("""
    Extract any remaining observations or notes not captured by other fields.
    This is a catch-all for data that does not fit elsewhere.
        ✅ Include: field notes, specimen condition, phenology observations,
            collection circumstances, or any other remarks.
        ❌ DO NOT include: habitat, locality, associated taxa, flower/fruit
            color, determiner/verifier, collector, dates, coordinates,
            elevation, or scientific name — those have their own fields.
    If no remarks are present, return an empty string.
    """)


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
