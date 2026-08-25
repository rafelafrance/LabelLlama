from dataclasses import InitVar, dataclass
from typing import ClassVar

from llama.pylib.base_field import BaseField


@dataclass
class LlmField(BaseField):
    description: ClassVar[str] = ""
    text: InitVar[str] = ""
