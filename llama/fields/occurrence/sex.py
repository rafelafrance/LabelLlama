import re
from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Sex(BaseField):
    sex: str = ""

    def __post_init__(self) -> None:
        self.sex = fix_parses.to_str(self.sex)

        sex = set()

        if re.search(r"♂♀|♀♂|pair|fm|mf", self.sex, flags=re.IGNORECASE):
            sex |= {"male", "female"}

        if re.search(r"\bm|♂", self.sex, flags=re.IGNORECASE) and "male" not in sex:
            sex.add("male")

        if re.search(r"\bf|♀", self.sex, flags=re.IGNORECASE) and "female" not in sex:
            sex.add("female")

        self.sex = " & ".join(sorted(sex, reverse=True)) if sex else self.sex
