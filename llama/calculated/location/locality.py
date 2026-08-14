import re
from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.calculated.calculated_field import CalculatedField


@dataclass
class Locality(CalculatedField):
    # --------------
    scoring_method: ClassVar[str] = "FPR"
    # --------------

    locality: str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Remove country, state/province, and county."""
        cleaned_rec = cleaned_rec or {}

        for field_name in ("country", "stateProvince", "county"):
            if value := cleaned_rec.get(field_name):
                # Remove the field from this string
                pattern = re.escape(str(value))
                self.locality = re.sub(pattern, "", self.locality, flags=re.IGNORECASE)

        self.locality = re.sub(
            r"\b(co\.?|county)\b", "", self.locality, flags=re.IGNORECASE
        )

        self.locality = self.clean_str_ends(self.locality)
        self.locality = " ".join(self.locality.split())

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
