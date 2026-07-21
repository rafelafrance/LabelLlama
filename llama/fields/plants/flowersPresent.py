import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class FlowersPresent(BaseField):
    flowersPresent: bool | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.flowersPresent = fix_parses.to_bool(self.flowersPresent)

        # Handle the case where the word "flowers" is being used as true
        if not self.flowersPresent:
            string = fix_parses.to_str(self.flowersPresent)
            self.flowersPresent = bool(
                re.search(r"(fls|flower|fl)", string, flags=re.IGNORECASE)
            )

        self.flowersPresent = self.flowersPresent or ""
