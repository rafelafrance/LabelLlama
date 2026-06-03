from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values, str_util


@dataclass
class AssociatedTaxa(BaseField):
    associatedTaxa: str = ""

    def __post_init__(self, text: str) -> None:
        del text

        self.associatedTaxa = fix_values.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = fix_values.remove_trailing_punct(self.associatedTaxa)
        self.associatedTaxa = str_util.compress(self.associatedTaxa)
