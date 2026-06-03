from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class InfraspecificEpithetAuthorship(BaseField):
    infraspecificEpithetAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithetAuthorship = fix_values.to_str(
            self.infraspecificEpithetAuthorship
        )
        self.infraspecificEpithetAuthorship = fix_values.clean_str_ends(
            self.infraspecificEpithetAuthorship
        )
