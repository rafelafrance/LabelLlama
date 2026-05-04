from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

DATE_IDENTIFIED: str = compress("""
    `dateIdentified` (str):
    Extract the date the specimen was identified, verified, or determined.
    This may be a full date (e.g., '1995-03-15') or a partial date
    (e.g., '1995', 'March 1995', '2001').
    Exclude the date label itself (e.g., words starting with 'date').
    If no identification date is present, return an empty string.
    """)


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

        # self.dateIdentified = fix_values.date_to_iso(self.dateIdentified)
