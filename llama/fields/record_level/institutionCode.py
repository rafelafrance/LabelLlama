from dataclasses import dataclass

from llama.fields.extracted_field import ExtractedField
from llama.pylib import fix_parses


@dataclass
class InstitutionCode(ExtractedField):
    institutionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.institutionCode = fix_parses.to_str(self.institutionCode)
