import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class VerbatimElevation(ExtractedField):
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
