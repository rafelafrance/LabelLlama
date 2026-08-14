from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class FruitPresent(CalculatedField):
    fruitPresent: bool | str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Set fruitPresent to True if there are fruit colors."""
        cleaned_rec = cleaned_rec or {}

        if not self.fruitPresent and (
            cleaned_rec["fruitColor"] or cleaned_rec["fruitFacts"]
        ):
            self.fruitPresent = True
