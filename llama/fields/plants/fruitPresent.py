import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class FruitPresent(ExtractedField):
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
