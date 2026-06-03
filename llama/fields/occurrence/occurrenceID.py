import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class OccurrenceID(BaseField):
    occurrenceID: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.occurrenceID = fix_values.to_str(self.occurrenceID)
        self.occurrenceID = re.sub(r"(#|Nº)", "", self.occurrenceID)

        # Remove the label
        self.occurrenceID = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*", "", self.occurrenceID, flags=re.IGNORECASE
        ).strip()
