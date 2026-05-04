from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

HABITAT: str = compress("""
    Extract the habitat or environment where the specimen grows.
    Describe the physical conditions and setting, not the location.
        ✅ Include: substrate ('dry sand', 'loamy soil', 'rocky outcrop'),
            vegetation type ('open grassland', 'mixed forest', 'shrubland'),
            hydrology ('wetland', 'stream bank', 'riparian'),
            disturbance ('roadside', 'old field', 'disturbed ground'),
            and life zones ('desert', 'prairie', 'alpine meadow').
        ❌ DO NOT include associated taxa — those belong to associatedTaxa.
        ❌ DO NOT include place names, geographic features, road names,
            or 'near [named place]' — those belong to locality.
        ❌ DO NOT include details about the plant itself (height, color, flowers).
    If no habitat information is present, return an empty string.
    """)


@dataclass
class Habitat(BaseField):
    habitat: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.habitat = fix_values.to_str(self.habitat)

        # Remove the habitat label
        words = self.habitat.split()
        words = [s for s in words if not s.lower().startswith("habitat")]
        self.habitat = " ".join(words)

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
