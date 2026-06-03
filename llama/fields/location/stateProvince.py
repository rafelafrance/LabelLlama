import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values

LABELS = re.compile(r"\s*(Departamento de|District|Provincia de)\s*", re.IGNORECASE)


@dataclass
class StateProvince(BaseField):
    stateProvince: str = ""

    def __post_init__(self, text: str) -> None:
        self.stateProvince = fix_values.hallucinated_str(self.stateProvince, text)
        self.stateProvince = fix_values.title_with_exceptions(self.stateProvince)
        self.stateProvince = LABELS.sub("", self.stateProvince)
