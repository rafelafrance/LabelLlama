import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class UtmZone(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the zone portion of the Universal Transverse Mercator (UTM) coordinates
        """
    # --------------

    utmZone: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utmZone = self.to_str(self.utmZone)
        self.utmZone = re.sub(r"\b(zone|z\.?)\b", "", self.utmZone).strip()
