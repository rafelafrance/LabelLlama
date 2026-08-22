from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class PlantHeight(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the overall plant height exactly as written, including units and ranges.
        Do not include dimensions of individual plant parts.
        """
    # --------------

    plantHeight: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.plantHeight = self.to_str(self.plantHeight)
