import re
from dataclasses import dataclass, field
from typing import Any

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

FRUIT_PRESENT: str = compress("""Is there fruit on the plant?""")


@dataclass
class FruitPresent(BaseField):
    fruitPresent: bool | str | None = field(default=False, metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.fruitPresent = fix_values.to_bool(self.fruitPresent)

        # Handle the case where the word "fruits" is being used as true
        if not self.fruitPresent:
            string = fix_values.to_str(self.fruitPresent)
            self.fruitPresent = bool(
                re.search(r"(fr|fruit)", string, flags=re.IGNORECASE)
            )

        self.fruitPresent = self.fruitPresent or ""

    def cross_field_update(self, record: dict[str, Any]) -> None:
        """Set fruitPresent to True if there are fruit colors."""
        if not self.fruitPresent and record["fruitColor"]:
            self.fruitPresent = True
