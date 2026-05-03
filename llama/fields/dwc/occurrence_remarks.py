import re
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.pylib import fix_values
from llama.pylib.str_util import dedent
from llama.fields.base_field import BOTH, BaseField

MIN_WORDS = 2
SKIP_FIELDS = ("occurrenceRemarks", "associatedTaxa")

OCCURRENCE_REMARKS: str = dedent(
    """
        This contains all other observations not in the other fields.
        ✅ Only include information not in other fields.
        ✅ This is strictly for data that is not covered anywhere else.
        ❌ DO NOT include habitat information.
        ❌ DO NOT include locality information.
        ❌ DO NOT include associated taxa information.
        ❌ DO NOT include flower color.
        ❌ DO NOT include the determiner or verifier.
        """,
)


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
