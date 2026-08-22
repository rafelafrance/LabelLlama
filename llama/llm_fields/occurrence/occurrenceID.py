import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class OccurrenceID(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the globally unique occurrence identifier when explicitly present, such
        as a UUID, URI, GUID, or occurrenceID. Do not use a plain catalog number unless
        it is labeled as the occurrence ID.
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
