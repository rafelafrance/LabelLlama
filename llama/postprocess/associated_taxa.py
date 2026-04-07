from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class AssociatedTaxa(BaseField):
    associatedTaxa: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.associatedTaxa = fix_values.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = fix_values.remove_trailing_punct(self.associatedTaxa)
