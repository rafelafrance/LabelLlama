from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class GeodeticDatum(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the geodetic datum used for the latitude, longitude, TRS, or UTM
        coordinates
        """
    # --------------

    geodeticDatum: str = ""

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = self.hallucinated_str(self.geodeticDatum, text)
