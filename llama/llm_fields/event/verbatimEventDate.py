import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VerbatimEventDate(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the collection date as written. Do not use the identification date.
        """
    # --------------

    verbatimEventDate: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.verbatimEventDate = self.to_str(self.verbatimEventDate)

        # Remove the date label
        self.verbatimEventDate = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.verbatimEventDate, flags=re.IGNORECASE
        ).strip()

        # Keep the "|" separator: the EventDate calc field splits on it to
        # normalize each part of a date range to ISO.
