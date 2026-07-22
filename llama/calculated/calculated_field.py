from dataclasses import InitVar, dataclass, field
from typing import Any

from llama.pylib.base_field import BaseField


@dataclass
class CalculatedField(BaseField):
    record: InitVar[dict[str, Any]] = field(default_factory=dict)
