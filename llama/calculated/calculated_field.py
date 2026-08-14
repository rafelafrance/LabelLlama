from dataclasses import InitVar, dataclass
from typing import Any

from llama.pylib.base_field import BaseField


@dataclass
class CalculatedField(BaseField):
    cleaned_rec: InitVar[dict[str, Any] | None] = None
