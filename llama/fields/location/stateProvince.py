import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses

LABELS = re.compile(r"\s*(Departamento de|District|Provincia de)\s*", re.IGNORECASE)


@dataclass
class StateProvince(BaseField):
    stateProvince: str = ""

    def __post_init__(self) -> None:
        self.stateProvince = fix_parses.to_str(self.stateProvince)
        self.stateProvince = fix_parses.title_with_exceptions(self.stateProvince)
        self.stateProvince = LABELS.sub("", self.stateProvince)
