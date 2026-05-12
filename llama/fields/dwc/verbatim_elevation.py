from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

VERBATIM_ELEVATION: str = compress("""
    `verbatimElevation` (str):
    Extract the verbatim elevation or altitude at which the specimen was collected.
    This may include the numeric value, units, and any labels (e.g., 'elev.', 'alt.',
    'altitude'). Preserve the text exactly as written.
    If no elevation information is present, return an empty string.
    """)

@dataclass
class VerbatimElevation(BaseField):
    verbatimElevation: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.verbatimElevation = fix_values.to_str(self.verbatimElevation)

        # Remove the label
        words = self.verbatimElevation.split()
        words = [w for w in words if not w.lower().startswith("el")]
        words = [w for w in words if not w.lower().startswith("alt")]
        self.verbatimElevation = " ".join(words)
