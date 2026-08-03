from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class EventDate(CalculatedField):
    eventDate: str = ""

    def __post_init__(self, record: dict[str, Any]) -> None:
        event_date = self.to_str(record.get("verbatimEventDate"))

        # Handle date ranges
        dates = event_date.split("|")
        dates = [self.date_to_iso(d) for d in dates]

        self.eventDate = self.eventDate.replace("|", " to ")
