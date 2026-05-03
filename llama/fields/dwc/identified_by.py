from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

IDENTIFIED_BY: str = compress("""
    Extract the name of the person who identified, verified, or determined the
    species of the specimen. This may appear with labels like 'det.', 'det. by',
    'id.', 'identified by', or 'verified by'.
    Preserve the name as written — do not expand abbreviations.
    If no identifier is named, return the default value.
    """)


@dataclass
class IdentifiedBy(BaseField):
    identifiedBy: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.identifiedBy = fix_values.to_str(self.identifiedBy)
