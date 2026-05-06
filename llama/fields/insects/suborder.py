from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SUBORDER: str = compress("""
    `suborder` (str):
    Extract the taxonomic suborder of the specimen (e.g., 'Cicindelina',
    'Faboideae', 'Nepenthodoideae'). The suborder ranks between order and
    family.
    It is distinct from order (a higher rank) and family (a lower rank).

    Suborder may appear with an explicit label such as 'subord.',
    'subord. Cicindelina', or simply as a standalone taxonomic name.

    Return the suborder name only — do not include the order, family,
    genus, specific epithet, authorship citations, or any other taxonomic
    rank.

    If no suborder is stated, return an empty string.
    """)


@dataclass
class Suborder(BaseField):
    suborder: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.suborder = fix_values.hallucinated_str(self.suborder, text)
