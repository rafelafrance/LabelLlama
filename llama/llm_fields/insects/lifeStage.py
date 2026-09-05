from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LifeStage(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the developmental or phenological stage of the insect specimen at the
        time of collection
        """
    # --------------

    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = self.hallucinated_str(self.lifeStage, text)
