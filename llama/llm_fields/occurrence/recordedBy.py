import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class RecordedBy(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the collector or observer, often indicated by leg., coll., collected by,
        or similar text.
        """
    # --------------

    recordedBy: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.recordedBy = self.to_str(self.recordedBy)

        # Remove the collector label
        self.recordedBy = re.sub(r"^(collector|coll?)\b[.:,;]?\s+", "", self.recordedBy)
        self.recordedBy = self.recordedBy.strip()
