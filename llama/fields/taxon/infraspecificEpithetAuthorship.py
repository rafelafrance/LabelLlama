from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class InfraspecificEpithetAuthorship(BaseField):
    infraspecificEpithetAuthorship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithetAuthorship = fix_parses.to_str(
            self.infraspecificEpithetAuthorship
        )
        self.infraspecificEpithetAuthorship = fix_parses.clean_str_ends(
            self.infraspecificEpithetAuthorship
        )
