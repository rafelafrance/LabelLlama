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

        # Handle date ranges
        dates = self.verbatimEventDate.split("|")
        dates = [self.date_to_iso(d) for d in dates]

        self.verbatimEventDate = self.verbatimEventDate.replace("|", " to ")
