import re
from dataclasses import dataclass
from typing import ClassVar

from llama.llm_fields.llm_field import LlmField


@dataclass
class Sex(LlmField):
    # --------------
    description: ClassVar[str] = """
        Extract the biological sex of the specimen as recorded on the label
        """
    # --------------

    sex: str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.sex = self.to_str(self.sex)

        sex = set()

        if re.search(r"♂♀|♀♂|pair|fm|mf", self.sex, flags=re.IGNORECASE):
            sex |= {"male", "female"}

        if re.search(r"\bm|♂", self.sex, flags=re.IGNORECASE) and "male" not in sex:
            sex.add("male")

        if re.search(r"\bf|♀", self.sex, flags=re.IGNORECASE) and "female" not in sex:
            sex.add("female")

        self.sex = " & ".join(sorted(sex, reverse=True)) if sex else self.sex
