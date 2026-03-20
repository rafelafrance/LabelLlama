from calendar import IllegalMonthError
from dataclasses import dataclass, field

from dateutil import parser

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, OUT, BaseField


@dataclass
class EventDate(BaseField):
    verbatimEventDate: str = field(default="", metadata=BOTH)
    eventDate: str = field(default="", metadata=OUT)

    def __post_init__(self) -> None:
        self.verbatimEventDate = fix_values.to_str(self.verbatimEventDate)

        words = self.verbatimEventDate.split()
        words = [w for w in words if not w.lower().startswith("date")]
        self.verbatimEventDate = " ".join(words)

        try:
            date_ = parser.parse(self.verbatimEventDate).date()
            self.eventDate = date_.isoformat()[:10]
        except parser.ParserError, IllegalMonthError:
            self.eventDate = ""
