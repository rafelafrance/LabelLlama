from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

LOCALITY: str = compress("""
    Extract the locality — the specific place or geographic description where
    the specimen was collected. This may include multiple phrases joined by
    commas or conjunctions.
        ✅ Include: place names, geographic features, road names, distances
            from towns, landmarks, and field-level descriptions.
        ❌ DO NOT include: TRS coordinates, UTM coordinates, elevation,
            county, state/province, or country — those have their own fields.
        ❌ DO NOT include: habitat descriptions (e.g., 'wetland', 'grassland')
            or associated taxa — those have their own fields.
    If no locality is present, return the default value.
    """)


@dataclass
class Locality(BaseField):
    locality: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.locality = fix_values.to_str(self.locality)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
