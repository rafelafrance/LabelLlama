import re
from dataclasses import dataclass
from typing import Any, ClassVar

from rapidfuzz import fuzz

from llama.llm_fields.llm_field import LlmField


@dataclass
class Habitat(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract ecological or environmental habitat descriptions.
        """
    scoring_method: ClassVar[str] = "FPR"
    # --------------

    habitat: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.habitat = self.to_str(self.habitat)

        # Remove the habitat label
        self.habitat = re.sub(
            r"^habitat[:,.;\s]*", "", self.habitat, flags=re.IGNORECASE
        ).strip()

    @staticmethod
    def score(expect: Any, actual: Any, record: dict[str, Any]) -> float:
        del record

        expect = str(expect)
        return fuzz.partial_ratio(expect, actual) / 100.0
