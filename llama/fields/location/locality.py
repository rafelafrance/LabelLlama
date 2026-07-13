import re
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

    def __post_init__(self) -> None:
        self.locality = fix_parses.to_str(self.locality)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Remove country, state/province, and county."""
        for field_name in ("country", "stateProvince", "county"):
            if value := record.get(field_name):
                # Remove the field from this string
                pattern = re.escape(str(value))
                self.locality = re.sub(pattern, "", self.locality, flags=re.IGNORECASE)

        self.locality = re.sub(
            r"\b(co\.?|county)\b", "", self.locality, flags=re.IGNORECASE
        )

        self.locality = fix_parses.clean_str_ends(self.locality)
        self.locality = " ".join(self.locality.split())

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
