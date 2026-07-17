from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class FruitPresent(CalculatedField):
    fruitPresent: bool | str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        """Set fruitPresent to True if there are fruit colors."""
        if not self.fruitPresent and (record["fruitColor"] or record["fruitFacts"]):
            self.fruitPresent = True
