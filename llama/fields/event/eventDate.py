import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class EventDate(ExtractedField):
    eventDate: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.eventDate = self.to_str(self.eventDate)

        # Remove the date label
        self.eventDate = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.eventDate, flags=re.IGNORECASE
        ).strip()

        # Handle date ranges
        dates = self.eventDate.split("|")
        dates = [self.date_to_iso(d) for d in dates]

        self.eventDate = self.eventDate or " to ".join(dates)
