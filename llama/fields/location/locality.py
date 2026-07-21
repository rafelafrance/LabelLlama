from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Locality(BaseField):
    # --------------
    scoring_method: ClassVar[str] = "FPR"
    # --------------

    locality: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.locality = fix_parses.to_str(self.locality)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
