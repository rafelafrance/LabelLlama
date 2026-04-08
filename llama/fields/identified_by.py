from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

IDENTIFIED_BY: str = compress("""
    Who identified or verified or determined the species.
    The identifier or verifier or determiner of the species.
    """)


@dataclass
class IdentifiedBy(BaseField):
    identifiedBy: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedBy = fix_values.to_str(self.identifiedBy)


DEFAULTS = {f.name: f.default for f in fields(IdentifiedBy)}
