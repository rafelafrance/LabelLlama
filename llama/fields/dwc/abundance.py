from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

ABUNDANCE: str = compress("""
    How common is the specimen?
    Examples include "common", "scattered", "rare."
    """)


@dataclass
class Abundance(BaseField):
    abundance: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.abundance = fix_values.hallucinated_str(self.abundance, text)
        self.abundance = fix_values.remove_trailing_punct(self.abundance)
