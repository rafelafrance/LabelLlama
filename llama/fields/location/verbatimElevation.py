import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class VerbatimElevation(BaseField):
    verbatimElevation: str = ""
    # elevation: float | str = ""
    # minimumElevation: float | str = ""
    # maximumElevation: float | str = ""
    # elevationUnits: str = ""
    # elevationEstimated: bool | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)

        # Remove the label
        self.verbatimElevation = re.sub(
            r"\b(el\w*|alt\w*)\b[:,.;\s]*",
            "",
            self.verbatimElevation,
            flags=re.IGNORECASE,
        ).strip()
