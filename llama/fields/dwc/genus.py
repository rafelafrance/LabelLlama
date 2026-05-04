from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

GENUS: str = compress("""
    `genus` (str):
    Extract the taxonomic genus of the specimen (e.g., 'Canis', 'Salix',
    'Agoseris', 'Drosophila'). The genus is the first component of the
    scientific name and is typically capitalized.

    Return the genus name only — do not include the specific epithet
    (e.g., from 'Canis lupus' extract 'Canis', not 'Canis lupus'),
    subgenus (e.g., from 'Aedes (Finlaya) aegypti' extract 'Aedes'),
    authorship citations (e.g., 'L.', 'Smith'), higher ranks (e.g.,
    family names), or any infraspecific epithets.

    If the genus name is preceded by a hybrid symbol (×), include it
    (e.g., '×Rhododendron').

    If multiple identifications are present, extract the genus from the
    primary (most specific) identification.

    If no genus is stated, return an empty string.
    """)


@dataclass
class Genus(BaseField):
    genus: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.genus = fix_values.to_str(self.genus)
