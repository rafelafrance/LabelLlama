from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class LifeCycle(BaseField):
    lifeCycle: str = ""

    def __post_init__(self, text: str) -> None:
        self.lifeCycle = fix_parses.hallucinated_str(self.lifeCycle, text)
