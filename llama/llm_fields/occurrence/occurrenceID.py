import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class OccurrenceID(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the catalog number — the unique identifier for the specimen or record
        within its collection or data set
        """
    # --------------

    occurrenceID: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.occurrenceID = self.to_str(self.occurrenceID)
        self.occurrenceID = re.sub(r"(#|Nº)", "", self.occurrenceID)

        # Remove the label
        self.occurrenceID = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*", "", self.occurrenceID, flags=re.IGNORECASE
        ).strip()
