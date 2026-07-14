import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Elevation(BaseField):
    elevation: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.elevation = fix_parses.to_str(self.elevation)
        self.clean_verbatim_elevation()

    def clean_verbatim_elevation(self) -> None:
        # Remove the label
        self.elevation = re.sub(
            r"\b(el\w*|alt\w*)\b[:,.;\s]*",
            "",
            self.elevation,
            flags=re.IGNORECASE,
        ).strip()
