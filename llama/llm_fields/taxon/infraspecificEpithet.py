from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class InfraspecificEpithet(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the infraspecific epithet from a subspecies, variety, form, or
        cultivar name. Do not include rank markers, genus, species epithet,
        or authorship.
        """
    # --------------

    infraspecificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithet = self.to_str(self.infraspecificEpithet).lower()
