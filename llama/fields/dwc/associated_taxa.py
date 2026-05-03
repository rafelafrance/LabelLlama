from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ASSOCIATED_TAXA: str = compress("""
    Extract the name(s) of other species found with or near the specimen.
    This may include host plants, epiphyte substrates, co-occurring species,
    or any other taxa mentioned in relation to the collection.
    If no associated taxa are mentioned, return an empty string.
    """)


@dataclass
class AssociatedTaxa(BaseField):
    associatedTaxa: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.associatedTaxa = fix_values.to_str(self.associatedTaxa)
        self.associatedTaxa = self.associatedTaxa.replace("*", "")
        self.associatedTaxa = fix_values.remove_trailing_punct(self.associatedTaxa)
