from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Country(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the country where the specimen was collected. Return the full, standard
        English country name
        """
    # --------------

    country: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.country = self.title_with_exceptions(self.country)
