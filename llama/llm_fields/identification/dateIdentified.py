import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class DateIdentified(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the date (or date range) when the specimen was identified, verified, or
        determined
        """
    # --------------

    dateIdentified: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.dateIdentified = self.to_str(self.dateIdentified)

        # Remove the date label
        self.dateIdentified = re.sub(
            r"\bdate\b[:,.;\s]*", "", self.dateIdentified, flags=re.IGNORECASE
        ).strip()
