import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class DateIdentified(ExtractedField):
    dateIdentified: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.dateIdentified = fix_parses.to_str(self.dateIdentified)

        # Remove the date label
        self.dateIdentified = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.dateIdentified, flags=re.IGNORECASE
        ).strip()
