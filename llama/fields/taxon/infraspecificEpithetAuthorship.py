from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class InfraspecificEpithetAuthorship(ExtractedField):
    infraspecificEpithetAuthorship: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.infraspecificEpithetAuthorship = self.to_str(
            self.infraspecificEpithetAuthorship
        )
        self.infraspecificEpithetAuthorship = self.clean_str_ends(
            self.infraspecificEpithetAuthorship
        )
