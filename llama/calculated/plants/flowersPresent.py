from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class FlowersPresent(CalculatedField):
    flowersPresent: bool | str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Set flowersPresent to True if there are flower colors or facts."""
        cleaned_rec = cleaned_rec or {}

        if not self.flowersPresent and (
            cleaned_rec["flowerColor"] or cleaned_rec["flowerFacts"]
        ):
            self.flowersPresent = True
