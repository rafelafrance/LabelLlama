from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

INFRASPECIFIC_EPITHET: str = compress("""
    Extract the infraspecific epithet (subspecies or variety name) from the
    scientific name. This is the third name after the genus and species,
    e.g., 'var. latifolia' or 'subsp. montana'.
    Return only the epithet itself — do not include the rank indicator
    ('var.', 'subsp.', 'forma', 'f.').
    If no infraspecific epithet is present, return the default value.
    """)


@dataclass
class InfraspecificEpithet(BaseField):
    infraspecificEpithet: str | None = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.infraspecificEpithet = fix_values.to_str(self.infraspecificEpithet).lower()
