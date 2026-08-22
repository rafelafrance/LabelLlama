from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Utm(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the complete Universal Transverse Mercator coordinate string exactly as
        written, including zone, easting, northing, hemisphere, datum, and units when
        present.
        """
    # --------------

    utm: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.utm = self.to_str(self.utm)
