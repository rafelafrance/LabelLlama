from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SUBGENUS: str = compress("""
    `subgenus` str:
    Extract the taxonomic subgenus of the specimen.
    The subgenus name is typically the first word of the scientific name on the label.
    Return the subgenus name only — do not include higher or lower ranks.
    If no subgenus is stated, return an empty string.
    """)


@dataclass
class Subgenus(BaseField):
    subgenus: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.subgenus = fix_values.to_str(self.subgenus)
