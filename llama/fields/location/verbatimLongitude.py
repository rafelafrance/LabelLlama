from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class VerbatimLongitude(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the longitude at which the specimen was collected
        """
    # --------------

    verbatimLongitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimLongitude = self.to_str(self.verbatimLongitude)
