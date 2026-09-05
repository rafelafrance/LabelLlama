from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Genus(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the taxonomic genus of the specimen (e.g., 'Canis', 'Salix', 'Agoseris',
        'Drosophila')
        """
    # --------------

    genus: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.genus = self.to_str(self.genus).capitalize()
