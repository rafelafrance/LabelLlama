import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class TrsQuad(BaseField):
    trsQuad: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.trsQuad = fix_values.to_str(self.trsQuad)

        # Remove quad label
        self.trsQuad = re.sub(r"\b(quad\w*|q\.?)\b", "", self.trsQuad).strip()
