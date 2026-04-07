from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class DateIdentified(BaseField):
    dateIdentified: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.dateIdentified = fix_values.to_str(self.dateIdentified)

        # Remove the date label
        words = self.dateIdentified.split()
        words = [w for w in words if not w.lower().startswith("date")]
        self.dateIdentified = " ".join(words)

        self.dateIdentified = fix_values.date_to_iso(self.dateIdentified)
