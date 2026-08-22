import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class TrsRange(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the range portion of a Township-Range-Section location, such as R4E
        or Range 4 East. Do not include township or section values.
        """
    # --------------

    trsRange: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsRange = self.to_str(self.trsRange)
        self.trsRange = re.sub(r"^r\s*", "", self.trsRange, flags=re.IGNORECASE)
