import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class UtmEasting(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the UTM easting value exactly as written. Do not include the zone
        or northing value.
        """
    # --------------

    utmEasting: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmEasting = self.to_str(self.utmEasting)
        # Drop only a trailing hemisphere marker (e.g. "123456 E"), leaving
        # the value and any other text untouched.
        self.utmEasting = re.sub(r"\s*[en]$", "", self.utmEasting, flags=re.IGNORECASE)
        self.utmEasting = "" if self.utmEasting in EMPTY_NE else self.utmEasting
