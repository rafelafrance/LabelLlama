from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class AssociatedTaxa(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the name(s) of other species found with or near the specimen.
        This field captures taxa associated with the collection but not the primary
        specimen itself
        """
    # --------------

    associatedTaxa: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.associatedTaxa = self.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = self.remove_trailing_punct(self.associatedTaxa)
        self.associatedTaxa = " ".join(self.associatedTaxa.split())
