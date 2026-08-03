from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class InfraspecificEpithet(ExtractedField):
    infraspecificEpithet: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithet = self.to_str(self.infraspecificEpithet).lower()
