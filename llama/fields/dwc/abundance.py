from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

ABUNDANCE: str = compress("""
    How common is the specimen?
    Examples include "common", "scattered", "rare."
    """)


@dataclass
class Abundance(BaseField):
    abundance: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.abundance = fix_values.to_str(self.abundance)
        self.abundance = fix_values.remove_trailing_punct(self.abundance)


DEFAULTS = DotDict({f.name: f.default for f in fields(Abundance)})
