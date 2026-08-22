from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class WaterBody(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract named rivers, streams, creeks, lakes, ponds, marshes, swamps, springs,
        sloughs, or similar water bodies.
        """
    # --------------

    waterBody: str = ""

    def __post_init__(self, text: str) -> None:
        self.waterBody = self.hallucinated_str(self.waterBody, text)
