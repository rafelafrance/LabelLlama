import re
from dataclasses import dataclass
from typing import Any

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class FlowersPresent(BaseField):
    flowersPresent: bool | str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.flowersPresent = fix_values.to_bool(self.flowersPresent)

        # Handle the case where the word "flowers" is being used as true
        if not self.flowersPresent:
            string = fix_values.to_str(self.flowersPresent)
            self.flowersPresent = bool(
                re.search(r"(fls|flower|fl)", string, flags=re.IGNORECASE)
            )

        self.flowersPresent = self.flowersPresent or ""

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Set flowersPresent to True if there are flower colors."""
        if not self.flowersPresent and record["flowerColor"]:
            self.flowersPresent = True
