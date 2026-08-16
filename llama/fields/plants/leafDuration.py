from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class LeafDuration(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the leaf duration (how long the plant retains its leaves through the
        growing season and/or winter)
        """
    # --------------

    leafDuration: str = ""

    def __post_init__(self, text: str) -> None:
        self.leafDuration = self.hallucinated_str(self.leafDuration, text)
