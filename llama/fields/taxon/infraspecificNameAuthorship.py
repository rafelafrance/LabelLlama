from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class InfraspecificNameAuthorship(BaseField):
    infraspecificNameAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificNameAuthorship = fix_values.to_str(
            self.infraspecificNameAuthorship
        )
        self.infraspecificNameAuthorship = fix_values.clean_str_ends(
            self.infraspecificNameAuthorship
        )
