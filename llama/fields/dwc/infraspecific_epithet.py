from dataclasses import dataclass, field

from llama.pylib import fix_values
from llama.pylib.str_util import compress
from llama.fields.base_field import BOTH, BaseField

INFRASPECIFIC_EPITHET: str = compress("""
    Contains the subspecies or variety portion of the scientific name.
    """)


@dataclass
class InfraspecificEpithet(BaseField):
    infraspecificEpithet: str | None = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.infraspecificEpithet = fix_values.to_str(self.infraspecificEpithet).lower()
