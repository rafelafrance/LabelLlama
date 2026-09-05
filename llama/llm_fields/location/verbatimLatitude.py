from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VerbatimLatitude(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the latitude at which the specimen was collected
        """
    # --------------

    verbatimLatitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimLatitude = self.to_str(self.verbatimLatitude)
