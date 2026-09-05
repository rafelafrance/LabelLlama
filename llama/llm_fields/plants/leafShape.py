from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LeafShape(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the shape of the specimen's leaf
        """
    # --------------

    leafShape: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafShape = self.hallucinated_str(self.leafShape, text)
