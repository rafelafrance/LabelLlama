import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses

SOURCE_THRESHOLD = 75.0


@dataclass
class RecordNumber(BaseField):
    recordNumber: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.recordNumber = fix_parses.to_str(self.recordNumber)
        self.recordNumber = re.sub(r"(#|Nº)", "", self.recordNumber)

        # Remove the label
        self.recordNumber = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*", "", self.recordNumber, flags=re.IGNORECASE
        ).strip()
