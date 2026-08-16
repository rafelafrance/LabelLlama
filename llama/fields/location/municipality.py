from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Municipality(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the municipality — the city, town, village, or other populated place
        where the specimen was collected
        """
    # --------------

    municipality: str = ""

    def __post_init__(self, text: str) -> None:
        self.municipality = self.hallucinated_str(self.municipality, text)
