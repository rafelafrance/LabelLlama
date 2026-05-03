import re
from dataclasses import dataclass, field
from typing import Any

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

FLOWERS_PRESENT: str = compress("""
    Determine whether the specimen has flowers present.
    Look for indicators like 'in flower', 'blooming', 'fl.', 'fls',
    'flowers', 'flowering', or the presence of flower color descriptions.
    Return True if flowers are present, False otherwise.
    If no information about flowers is stated, return the default value.
    """)


@dataclass
class FlowersPresent(BaseField):
    flowersPresent: bool | str | None = field(default="", metadata=BOTH)

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
