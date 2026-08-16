from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class LeafMargin(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the description of the specimen's leaf margins (edge shape)
        """
    # --------------

    leafMargin: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafMargin = self.hallucinated_str(self.leafMargin, text)
