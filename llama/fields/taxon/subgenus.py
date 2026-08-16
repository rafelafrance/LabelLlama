from dataclasses import dataclass
from typing import ClassVar

from llama.fields.llm_field import LlmField


@dataclass
class Subgenus(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the taxonomic subgenus of the specimen (e.g., 'Finlaya', 'Leptalegia',
        'Caninae')
        """
    # --------------

    subgenus: str = ""

    def __post_init__(self, text: str) -> None:
        self.subgenus = self.hallucinated_str(self.subgenus, text)
