from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class GeodeticDatum(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the coordinate datum explicitly associated with the location, such as
        WGS84, NAD27, NAD83, or a named map datum. Do not infer a datum when it is not
        stated.
        """
    # --------------

    geodeticDatum: str = ""

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = self.hallucinated_str(self.geodeticDatum, text)
