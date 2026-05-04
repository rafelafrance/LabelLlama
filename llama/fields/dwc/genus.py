from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

GENUS: str = compress("""
    `genus` str:
    Extract the taxonomic genus of the specimen (e.g., 'Canis', 'Salix', 'Agoseris').
    The genus name is typically the first word of the scientific name on the label.
    Return the genus name only — do not include higher or lower ranks.
    If no genus is stated, return an empty string.
    """)


@dataclass
class Genus(BaseField):
    genus: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.genus = fix_values.to_str(self.genus)
