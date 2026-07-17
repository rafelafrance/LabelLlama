from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class FlowersPresent(CalculatedField):
    flowersPresent: bool | str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Set flowersPresent to True if there are flower colors or facts."""
        if not self.flowersPresent and (record["flowerColor"] or record["flowerFacts"]):
            self.flowersPresent = True
