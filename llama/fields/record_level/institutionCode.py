from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class InstitutionCode(BaseField):
    institutionCode: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.institutionCode = fix_values.to_str(self.institutionCode)
