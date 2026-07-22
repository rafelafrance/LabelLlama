from dataclasses import InitVar, dataclass

from llama.pylib.base_field import BaseField


@dataclass
class ExtractedField(BaseField):
    text: InitVar[str] = ""
