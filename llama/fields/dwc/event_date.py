from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

VERBATIM_EVENT_DATE: str = compress("""When was the specimen collected.""")


@dataclass
class EventDate(BaseField):
    verbatimEventDate: str = field(default="", metadata=BOTH)
    eventDate: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimEventDate = fix_values.to_str(self.verbatimEventDate)

        # Remove the event date label
        words = self.verbatimEventDate.split()
        words = [w for w in words if not w.lower().startswith("date")]
        self.verbatimEventDate = " ".join(words)

        self.eventDate = self.eventDate or fix_values.date_to_iso(
            self.verbatimEventDate
        )
