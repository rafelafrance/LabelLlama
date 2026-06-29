import re
from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Habitat(BaseField):
    # --------------
    scoring_method: ClassVar[str] = "FPR"
    # --------------

    habitat: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.habitat = fix_parses.to_str(self.habitat)

        # Remove the habitat label
        self.habitat = re.sub(
            r"^habitat[:,.;\s]*", "", self.habitat, flags=re.IGNORECASE
        ).strip()

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
