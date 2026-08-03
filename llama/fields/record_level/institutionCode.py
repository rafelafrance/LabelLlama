from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField


@dataclass
class InstitutionCode(ExtractedField):
    institutionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.institutionCode = self.to_str(self.institutionCode)
