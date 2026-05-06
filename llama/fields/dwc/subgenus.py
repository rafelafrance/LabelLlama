from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SUBGENUS: str = compress("""
    `subgenus` (str):
    Extract the taxonomic subgenus of the specimen (e.g., 'Finlaya',
    'Leptalegia', 'Caninae'). The subgenus ranks between genus and species.
    It is distinct from genus (the first word of the scientific name) and
    from section/series (lower ranks sometimes indicated by 'sect.' or
    'ser.').

    Subgenus is commonly written in parentheses between the genus and the
    specific epithet, e.g., 'Aedes (Finlaya) aegypti' — extract only
    'Finlaya'. It may also appear with an explicit label such as
    'subgen. Finlaya' or 'subg. Finlaya'.

    Return the subgenus name only — do not include the genus, specific
    epithet, authorship citations, or any other taxonomic rank.

    If no subgenus is stated, return an empty string.
    """)


@dataclass
class Subgenus(BaseField):
    subgenus: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.subgenus = fix_values.hallucinated_str(self.subgenus, text)
