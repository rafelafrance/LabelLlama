from dataclasses import InitVar, dataclass

from llama.pylib.base_field import BaseField


@dataclass
class LlmField(BaseField):
    text: InitVar[str] = ""
