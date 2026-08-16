from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class InfraspecificEpithetAuthorship(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the authorship citation for the infraspecific name (subspecies, variety,
        or form)
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
