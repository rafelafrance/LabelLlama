from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class IslandGroup(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the name of the island group, archipelago, or atoll group where the
        specimen was collected
        """
    # --------------

    islandGroup: str = ""

    def __post_init__(self, text: str) -> None:
        self.islandGroup = self.hallucinated_str(self.islandGroup, text)
