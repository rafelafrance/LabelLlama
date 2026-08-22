from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class SpecificEpithet(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the species epithet from the scientific name. Do not include genus,
        infraspecific epithets, authorship, or identification qualifiers.
        """
    # --------------

    specificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.specificEpithet = self.to_str(self.specificEpithet).lower()
