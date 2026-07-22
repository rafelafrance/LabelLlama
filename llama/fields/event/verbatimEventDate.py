import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class VerbatimEventDate(ExtractedField):
    verbatimEventDate: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimEventDate = fix_parses.to_str(self.verbatimEventDate)

        # Remove the date label
        self.verbatimEventDate = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.verbatimEventDate, flags=re.IGNORECASE
        ).strip()

        # Handle date ranges
        dates = self.verbatimEventDate.split("|")
        dates = [fix_parses.date_to_iso(d) for d in dates]

        self.verbatimEventDate = self.verbatimEventDate.replace("|", " to ")
