from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class VerbatimLongitude(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the longitude exactly as written.
        """
    # --------------

    verbatimLongitude: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimLongitude = self.to_str(self.verbatimLongitude)
