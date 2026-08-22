from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class InstitutionCode(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the owning institution code only if explicitly present or unambiguous.
        """
    # --------------

    institutionCode: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.institutionCode = self.to_str(self.institutionCode)
