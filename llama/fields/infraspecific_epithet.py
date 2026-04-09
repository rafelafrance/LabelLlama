from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
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


DEFAULTS = DotDict({f.name: f.default for f in fields(InfraspecificEpithet)})
