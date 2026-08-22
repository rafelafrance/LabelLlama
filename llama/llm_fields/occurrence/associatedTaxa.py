from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class AssociatedTaxa(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract taxa explicitly recorded as associated with the specimen or collection,
        such as host plants, substrates, nearby species, or associated organisms. Do not
        include the primary specimen taxon.
        """
    # --------------

    associatedTaxa: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.associatedTaxa = self.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = self.remove_trailing_punct(self.associatedTaxa)
        self.associatedTaxa = " ".join(self.associatedTaxa.split())
