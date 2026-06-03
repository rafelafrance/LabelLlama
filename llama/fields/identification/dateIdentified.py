import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class DateIdentified(BaseField):
    dateIdentified: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.dateIdentified = fix_values.to_str(self.dateIdentified)

        # Remove the date label
        self.dateIdentified = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.dateIdentified, flags=re.IGNORECASE
        )

        # self.dateIdentified = fix_values.date_to_iso(self.dateIdentified)
