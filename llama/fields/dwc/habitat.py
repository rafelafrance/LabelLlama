from dataclasses import dataclass, field
from typing import Any

from rapidfuzz import fuzz

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


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
