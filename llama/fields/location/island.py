from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Island(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the name(s) of the island(s) on or near which the specimen was collected
        """
    # --------------

    island: str = ""

    def __post_init__(self, text: str) -> None:
        self.island = self.hallucinated_str(self.island, text)
