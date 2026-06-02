import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, HIDE, BaseField
from llama.pylib import fix_values


@dataclass
class IdentifiedByID(BaseField):
    identifiedByID: str = field(default="", metadata=BOTH | HIDE)

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedByID = fix_values.to_str(self.identifiedByID)
        self.identifiedByID = re.sub(r"(#|Nº)", "", self.identifiedByID)

        # Remove the label
        self.identifiedByID = re.sub(
            r"\b(no|number|num)\b[:,.;\s]*",
            "",
            self.identifiedByID,
            flags=re.IGNORECASE,
        )
