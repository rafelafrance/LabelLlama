import re
from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class TrsTownship(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the township portion of the Township-Range-Section (TRS) coordinates
        """
    # --------------

    trsTownship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsTownship = self.to_str(self.trsTownship)
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
        self.trsTownship = self.trsTownship.strip()
