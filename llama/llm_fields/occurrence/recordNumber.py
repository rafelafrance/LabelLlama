import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField

SOURCE_THRESHOLD = 75.0


@dataclass
class RecordNumber(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the collector number, field number, station number, or event number. Do
        not use the catalog number.
        """
    # --------------

    recordNumber: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.recordNumber = self.to_str(self.recordNumber)
        self.recordNumber = re.sub(r"(#|Nº)", "", self.recordNumber)

        # Remove the label
        self.recordNumber = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*", "", self.recordNumber, flags=re.IGNORECASE
        ).strip()
