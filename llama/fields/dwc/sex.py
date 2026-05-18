import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values


@dataclass
class Sex(BaseField):
    sex: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.sex = fix_values.to_str(self.sex)

        sex = []

        if re.search(r"♂♀|♀♂|pair|fm|mf", self.sex, flags=re.IGNORECASE):
            sex += ["male", "female"]

        if re.search(r"\b[m]|♂", self.sex, flags=re.IGNORECASE) and "male" not in sex:
            sex.append("male")

        if re.search(r"\b[f]|♀", self.sex, flags=re.IGNORECASE) and "female" not in sex:
            sex.append("female")

        self.sex = " & ".join(sex) if sex else self.sex
