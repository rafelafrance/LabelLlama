from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class AssociatedTaxa(BaseField):
    associatedTaxa: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.associatedTaxa = fix_parses.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = fix_parses.remove_trailing_punct(self.associatedTaxa)
        self.associatedTaxa = " ".join(self.associatedTaxa.split())
