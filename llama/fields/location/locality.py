from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.fields.extracted_field import ExtractedField


@dataclass
class Locality(ExtractedField):
    # --------------
    scoring_method: ClassVar[str] = "FPR"
    # --------------

    locality: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.locality = self.to_str(self.locality)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
