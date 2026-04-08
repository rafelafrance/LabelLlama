from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

ASSOCIATED_TAXA: str = compress(
    """Was the specimen found near, around, or on another species."""
)


@dataclass
class AssociatedTaxa(BaseField):
    associatedTaxa: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.associatedTaxa = fix_values.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = fix_values.remove_trailing_punct(self.associatedTaxa)


DEFAULTS = {f.name: f.default for f in fields(AssociatedTaxa)}
