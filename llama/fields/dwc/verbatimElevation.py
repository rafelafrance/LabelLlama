import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class VerbatimElevation(BaseField):
    verbatimElevation: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)

        # Remove the label
        self.verbatimElevation = re.sub(
            r"(el\w*|alt\w*)[:,.;\s]*", "", self.verbatimElevation, flags=re.IGNORECASE
        )
