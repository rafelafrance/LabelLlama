from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class AssociatedTaxa(ExtractedField):
    associatedTaxa: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.associatedTaxa = self.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = self.remove_trailing_punct(self.associatedTaxa)
        self.associatedTaxa = " ".join(self.associatedTaxa.split())
