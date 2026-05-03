from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

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
