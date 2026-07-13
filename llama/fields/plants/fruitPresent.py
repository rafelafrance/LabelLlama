import re
from dataclasses import dataclass
from typing import Any

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FruitPresent(BaseField):
    fruitPresent: bool | str = ""

    def __post_init__(self) -> None:
        self.fruitPresent = fix_parses.to_bool(self.fruitPresent)

        # Handle the case where the word "fruits" is being used as true
        if not self.fruitPresent:
            string = fix_parses.to_str(self.fruitPresent)
            self.fruitPresent = bool(
                re.search(r"(fr|fruit)", string, flags=re.IGNORECASE)
            )

        self.fruitPresent = self.fruitPresent or ""

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Set fruitPresent to True if there are fruit colors."""
        if not self.fruitPresent and record["fruitColor"]:
            self.fruitPresent = True
