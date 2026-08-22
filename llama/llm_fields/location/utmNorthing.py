from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField

# Remove these extra values
EMPTY_NE: tuple = ("0", "0.0")


@dataclass
class UtmNorthing(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the UTM northing value exactly as written. Do not include the zone
        or easting value.
        """
    # --------------

    utmNorthing: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmNorthing = self.to_str(self.utmNorthing)
        self.utmNorthing = self.utmNorthing.lower().replace("n", "")
        self.utmNorthing = "" if self.utmNorthing in EMPTY_NE else self.utmNorthing
