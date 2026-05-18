from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class VerbatimEventDate(BaseField):
    verbatimEventDate: str = field(default="", metadata=BOTH)
    eventDate: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimEventDate = fix_values.to_str(self.verbatimEventDate)

        # Remove the event date label
        words = self.verbatimEventDate.split()
        words = [w for w in words if not w.lower().startswith("date")]
        self.verbatimEventDate = " ".join(words)

        dates = self.verbatimEventDate.split("|")
        dates = [fix_values.date_to_iso(d) for d in dates]

        self.verbatimEventDate = self.verbatimEventDate.replace("|", " to ")
        self.eventDate = self.eventDate or " to ".join(dates)
