import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VerbatimElevation(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract elevation or altitude exactly as written, including units, ranges, or
        greater-than/less-than symbols. Do not convert between meters and feet.
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
