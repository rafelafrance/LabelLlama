from dataclasses import dataclass, field

from rapidfuzz import fuzz

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class Habitat(BaseField):
    habitat: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.habitat = fix_values.to_str(self.habitat)

        # Remove the habitat label
        words = self.habitat.split()
        words = [s for s in words if not s.lower().startswith("habitat")]
        self.habitat = " ".join(words)

    @staticmethod
    def fuzzy_score(expect: str, actual: str) -> float:
        return fuzz.partial_ratio(expect, actual)
