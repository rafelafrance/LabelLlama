from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class WaterBody(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the name of the specific body of water where the specimen was collected
        """
    # --------------

    waterBody: str = ""

    def __post_init__(self, text: str) -> None:
        self.waterBody = self.hallucinated_str(self.waterBody, text)
