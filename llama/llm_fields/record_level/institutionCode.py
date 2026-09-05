from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class InstitutionCode(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the institution code — the acronym, coden, abbreviation, or initialism
        used by the institution that owns the specimen or data record
        """
    # --------------

    institutionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.institutionCode = self.to_str(self.institutionCode)
