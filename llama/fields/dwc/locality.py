from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

LOCALITY: str = compress("""
        Get the locality from input text string.
        There may be multiple phrases that describe the locality.
        Exclude the TRS, UTM, elevation, and county.
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
