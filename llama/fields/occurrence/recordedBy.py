import re
from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class RecordedBy(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the name of the person or group who collected or observed the specimen
        """
    # --------------

    recordedBy: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.recordedBy = self.to_str(self.recordedBy)

        # Remove the collector label
        self.recordedBy = re.sub(r"^(collector|coll?)\b[.:,;]?\s+", "", self.recordedBy)
        self.recordedBy = self.recordedBy.strip()
