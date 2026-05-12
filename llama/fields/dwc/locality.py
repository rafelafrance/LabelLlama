import re
from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LOCALITY: str = compress("""
    `locality` (str):
    Extract the locality — the specific place or geographic description where
    the specimen was collected. This may include multiple phrases joined by
    commas or conjunctions.
        ✅ Include: place names, geographic features, road names, distances
            from towns, landmarks, and field-level descriptions.
        ❌ DO NOT include: TRS coordinates, UTM coordinates, elevation,
            county, state/province, or country — those have their own fields.
        ❌ DO NOT include: habitat descriptions (e.g., 'wetland', 'grassland')
            or associated taxa — those have their own fields.
    If no locality is present, return an empty string.
    """)


@dataclass
class Locality(BaseField):
    locality: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.locality = fix_values.to_str(self.locality)

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Remove country, state/province, and county."""
        for field_name in ("country", "stateProvince", "county"):
            if value := record.get(field_name):
                # Remove the field from this string
                pattern = re.escape(str(value))
                self.locality = re.sub(pattern, "", self.locality, flags=re.IGNORECASE)

        self.locality = re.sub(
            r"co\.?|county", "", self.locality, flags=re.IGNORECASE
        )

        self.locality = fix_values.clean_str_ends(self.locality)
        self.locality = compress(self.locality)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
