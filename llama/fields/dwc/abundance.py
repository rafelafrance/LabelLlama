from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ABUNDANCE: str = compress("""
    Extract the abundance or frequency of the specimen at the collection site.
    This describes how common or rare the plant was where it was collected.
    Examples: "common", "abundant", "scattered", "rare", "occasional",
    "numerous", "uncommon", "few", "sparse", "dominant".
    If no abundance information is stated, return the default value.
    """)


@dataclass
class Abundance(BaseField):
    abundance: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.abundance = fix_values.hallucinated_str(self.abundance, text)
        self.abundance = fix_values.remove_trailing_punct(self.abundance)
