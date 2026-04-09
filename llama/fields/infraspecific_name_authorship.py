from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

INFRASPECIFIC_NAME_AUTHORSHIP: str = compress(
    """The author (authority) who coined the infraspecific name."""
)


@dataclass
class InfraspecificNameAuthorship(BaseField):
    infraspecificNameAuthorship: str | None = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.infraspecificNameAuthorship = fix_values.to_str(
            self.infraspecificNameAuthorship
        )


DEFAULTS = DotDict({f.name: f.default for f in fields(InfraspecificNameAuthorship)})
