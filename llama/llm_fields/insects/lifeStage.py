from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class LifeStage(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract insect life stage terms such as larva, nymph, exuvia, teneral, adult,
        or imago when present.
        """
    # --------------

    lifeStage: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeStage = self.hallucinated_str(self.lifeStage, text)
