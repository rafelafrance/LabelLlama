import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class VerbatimElevation(ExtractedField):
    verbatimElevation: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = fix_parses.to_str(self.verbatimElevation)

        # Remove the label
        self.verbatimElevation = re.sub(
            r"\b(el\w*|alt\w*)\b[:,.;\s]*",
            "",
            self.verbatimElevation,
            flags=re.IGNORECASE,
        ).strip()
