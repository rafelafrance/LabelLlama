import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class VerbatimElevation(BaseField):
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
