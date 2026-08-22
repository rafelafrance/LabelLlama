import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class TrsTownship(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the township portion of a Township-Range-Section location, such as
        T2N or Township 2 North. Do not include range or section values.
        """
    # --------------

    trsTownship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsTownship = self.to_str(self.trsTownship)
        self.trsTownship = re.sub(r"^t\s*", "", self.trsTownship, flags=re.IGNORECASE)
        self.trsTownship = self.trsTownship.strip()
