from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class IslandGroup(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the island group, archipelago, or atoll group where the specimen was
        collected. Do not use the individual island name unless no group is stated.
        """
    # --------------

    islandGroup: str = ""

    def __post_init__(self, text: str) -> None:
        self.islandGroup = self.hallucinated_str(self.islandGroup, text)
