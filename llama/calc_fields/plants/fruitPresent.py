from dataclasses import dataclass
from typing import Any

from llama.calc_fields.calc_field import CalcField


@dataclass
class FruitPresent(CalcField):
    fruitPresent: bool | str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        """Set fruitPresent to True if there are fruit colors."""
        cleaned_rec = cleaned_rec or {}

        if not self.fruitPresent and (
            cleaned_rec.get("fruitColor") or cleaned_rec.get("fruitFacts")
        ):
            self.fruitPresent = True
