from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, OUT, BaseField


@dataclass
class EventDate(BaseField):
    verbatimEventDate: str = field(default="", metadata=BOTH)
    eventDate: str = field(default="", metadata=OUT)

    def __post_init__(self) -> None:
        self.verbatimEventDate = fix_values.to_str(self.verbatimEventDate)

        # Remove the event date label
        words = self.verbatimEventDate.split()
        words = [w for w in words if not w.lower().startswith("date")]
        self.verbatimEventDate = " ".join(words)

        self.eventDate = fix_values.date_to_iso(self.verbatimEventDate)
