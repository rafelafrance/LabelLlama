from dataclasses import dataclass

from llama.fields.base_field import BaseField
from llama.pylib import fix_values


@dataclass
class ElevationEstimated(BaseField):
    elevationEstimated: bool | str = ""

    def __post_init__(self, text: str) -> None:
        del text
        self.elevationEstimated = fix_values.to_truthy(self.elevationEstimated)
