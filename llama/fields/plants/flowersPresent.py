import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class FlowersPresent(ExtractedField):
    flowersPresent: bool | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.flowersPresent = self.to_bool(self.flowersPresent)

        # Handle the case where the word "flowers" is being used as true
        if not self.flowersPresent:
            string = self.to_str(self.flowersPresent)
            self.flowersPresent = bool(
                re.search(r"(fls|flower|fl)", string, flags=re.IGNORECASE)
            )

        self.flowersPresent = self.flowersPresent or ""
