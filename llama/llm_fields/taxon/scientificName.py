import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class ScientificName(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the genus and species name only. Do not include authorship, sex, life
        stage, or determination labels.
        """
    # --------------

    scientificName: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.scientificName = self.to_str(self.scientificName)
        self.scientificName = re.sub(r"[^\w\s]", "", self.scientificName).strip()

        words = self.scientificName.split()
        if len(words) == 0:
            self.scientificName = ""
        elif len(words) == 1:
            self.scientificName = words[0].capitalize()
        else:
            genus, species, *_ = words
            self.scientificName = f"{genus.capitalize()} {species.lower()}"
