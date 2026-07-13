import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class EventDate(BaseField):
    eventDate: str = ""

    def __post_init__(self) -> None:
        self.eventDate = fix_parses.to_str(self.eventDate)

        # Remove the date label
        self.eventDate = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.eventDate, flags=re.IGNORECASE
        ).strip()

        # Handle date ranges
        dates = self.eventDate.split("|")
        dates = [fix_parses.date_to_iso(d) for d in dates]

        self.eventDate = self.eventDate or " to ".join(dates)
