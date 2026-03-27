from dataclasses import dataclass, field

from rapidfuzz import fuzz

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class Locality(BaseField):
    locality: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.locality = fix_values.to_str(self.locality)

    @staticmethod
    def fuzzy_score(expect: str, actual: str) -> float:
        return fuzz.partial_ratio(expect, actual) / 100.0
