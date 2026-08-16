from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.fields.llm_field import LlmField


@dataclass
class Locality(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the locality — the specific place or geographic description where the
        specimen was collected
        """
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
