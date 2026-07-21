import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FruitPresent(BaseField):
    fruitPresent: bool | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.fruitPresent = fix_parses.to_bool(self.fruitPresent)

        # Handle the case where the word "fruits" is being used as true
        if not self.fruitPresent:
            string = fix_parses.to_str(self.fruitPresent)
            self.fruitPresent = bool(
                re.search(r"(fr|fruit)", string, flags=re.IGNORECASE)
            )

        self.fruitPresent = self.fruitPresent or ""
