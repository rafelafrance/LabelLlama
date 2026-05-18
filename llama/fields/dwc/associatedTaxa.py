from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class AssociatedTaxa(BaseField):
    associatedTaxa: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.associatedTaxa = fix_values.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = fix_values.remove_trailing_punct(self.associatedTaxa)
