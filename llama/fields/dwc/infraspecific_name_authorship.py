from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

INFRASPECIFIC_NAME_AUTHORSHIP: str = compress("""
    Extract the authorship citation for the infraspecific name (subspecies or
    variety). This is the person(s) who originally described the subspecies or
    variety, separate from the species-level authorship.
    Authors may be abbreviated, sometimes to a single letter.
    If no infraspecific authorship is stated, return the default value.
    """)


@dataclass
class InfraspecificNameAuthorship(BaseField):
    infraspecificNameAuthorship: str | None = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.infraspecificNameAuthorship = fix_values.to_str(
            self.infraspecificNameAuthorship
        )
