from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class InfraspecificEpithet(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the infraspecific epithet (subspecies, variety, or form name) from the
        scientific name
        """
    # --------------

    infraspecificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithet = self.to_str(self.infraspecificEpithet).lower()
