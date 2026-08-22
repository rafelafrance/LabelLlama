from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Woodiness(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract woodiness or stem-texture terms, such as woody, herbaceous,
        suffrutescent, subshrub, shrub, tree, or vine, when explicitly stated.
        """
    # --------------

    woodiness: str = ""

    def __post_init__(self, text: str) -> None:
        self.woodiness = self.hallucinated_str(self.woodiness, text)
