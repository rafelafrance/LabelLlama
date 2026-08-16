from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class IdentifiedBy(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the name of the person or group who identified, determined, or verified
        the taxonomic name of the specimen. This is the determiner, not the original
        collector
        """
    # --------------

    identifiedBy: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedBy = self.to_str(self.identifiedBy)
