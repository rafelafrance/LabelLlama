import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class IdentifiedByID(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the globally unique identifier for the person, group, or organization
        responsible for assigning the taxon to the specimen.
        """
    # --------------

    identifiedByID: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedByID = self.to_str(self.identifiedByID)
        self.identifiedByID = re.sub(r"(#|Nº)", "", self.identifiedByID)

        # Remove the label
        self.identifiedByID = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*",
            "",
            self.identifiedByID,
            flags=re.IGNORECASE,
        ).strip()
