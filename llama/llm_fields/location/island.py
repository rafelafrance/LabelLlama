from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Island(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the island name where the specimen was collected. Do not use island
        group, archipelago, country, state, or province names unless they are the island
        name itself.
        """
    # --------------

    island: str = ""

    def __post_init__(self, text: str) -> None:
        self.island = self.hallucinated_str(self.island, text)
