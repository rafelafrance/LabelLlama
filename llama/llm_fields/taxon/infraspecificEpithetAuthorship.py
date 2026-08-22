from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class InfraspecificEpithetAuthorship(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract only the authorship citation associated with the infraspecific name. Do
        not include the epithet, rank marker, or species-level authorship.
        """
    # --------------

    infraspecificEpithetAuthorship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithetAuthorship = self.to_str(
            self.infraspecificEpithetAuthorship
        )
        self.infraspecificEpithetAuthorship = self.clean_str_ends(
            self.infraspecificEpithetAuthorship
        )
