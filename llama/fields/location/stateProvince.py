import re
from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField

LABELS = re.compile(r"\s*(Departamento de|District|Provincia de)\s*", re.IGNORECASE)


@dataclass
class StateProvince(ExtractedField):
    stateProvince: str = ""

    def __post_init__(self, text: str) -> None:
        self.stateProvince = self.hallucinated_str(self.stateProvince, text)
        self.stateProvince = self.title_with_exceptions(self.stateProvince)
        self.stateProvince = LABELS.sub("", self.stateProvince)
