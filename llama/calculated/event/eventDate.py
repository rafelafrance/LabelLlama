from dataclasses import dataclass
from typing import Any

from llama.calculated.calculated_field import CalculatedField


@dataclass
class EventDate(CalculatedField):
    eventDate: str = ""

    def __post_init__(self, cleaned_rec: dict[str, Any] | None) -> None:
        cleaned_rec = cleaned_rec or {}

        event_date = self.to_str(cleaned_rec.get("verbatimEventDate"))

        # Handle date ranges
        if event_date:
            dates = event_date.split("|")
            dates = [self.date_to_iso(d) for d in dates]
            self.eventDate = " to ".join(dates)
