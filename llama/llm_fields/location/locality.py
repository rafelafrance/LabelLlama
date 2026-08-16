from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.llm_fields.llm_field import LlmField


@dataclass
class Locality(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the locality — the specific place or geographic description where the
        specimen was collected.
        This does not include the country (which belongs in `country`),
        This does not include the stateProvince (which belongs in `stateProvince`),
        This does not include the county (which belongs in `county`).
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
