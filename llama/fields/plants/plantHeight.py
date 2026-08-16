from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class PlantHeight(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the overall height of the specimen or the plant as a whole
        """
    # --------------

    plantHeight: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.plantHeight = self.to_str(self.plantHeight)
