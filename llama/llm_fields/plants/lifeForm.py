from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LifeForm(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the ecological life form (aka niche) of the specimen
        """
    # --------------

    lifeForm: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeForm = self.hallucinated_str(self.lifeForm, text)
