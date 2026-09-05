import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VerbatimElevation(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the elevation or altitude at which the specimen was collected
        """
    # --------------

    verbatimElevation: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = self.to_str(self.verbatimElevation)

        # Remove the label
        self.verbatimElevation = re.sub(
            r"\b(el\w*|alt\w*)\b[:,.;\s]*",
            "",
            self.verbatimElevation,
            flags=re.IGNORECASE,
        ).strip()
