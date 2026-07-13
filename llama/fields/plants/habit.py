from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_parses


@dataclass
class Habit(BaseField):
    habit: str = ""

    def __post_init__(self) -> None:
        self.habit = fix_parses.to_str(self.habit)
