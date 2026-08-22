from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class IdentifiedBy(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the determiner or verifier, often indicated by det., determined by, ID
        by, or vid. This is the person or group who identified, determined, or verified
        the taxonomic name, not the original collector.
        """
    # --------------

    identifiedBy: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedBy = self.to_str(self.identifiedBy)
