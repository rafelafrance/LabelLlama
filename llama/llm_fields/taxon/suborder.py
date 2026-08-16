from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Suborder(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the taxonomic suborder of the specimen (e.g., 'Violineae',
        'Cucurbitineae', 'Heterodontina')
        """
    # --------------

    suborder: str = ""

    def __post_init__(self, text: str) -> None:
        self.suborder = self.hallucinated_str(self.suborder, text)
