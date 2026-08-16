import re
from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class TrsRange(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the range portion of the Township-Range-Section (TRS) coordinates
        """
    # --------------

    trsRange: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsRange = self.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)
