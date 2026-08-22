from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LifeStage(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract plant developmental or phenological stage terms, such as seedling,
        juvenile, vegetative, budding, flowering, fruiting, sterile, or senescent.
        """
    # --------------

    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = self.hallucinated_str(self.lifeStage, text)
