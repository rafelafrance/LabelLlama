from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class GeodeticDatum(BaseField):
    geodeticDatum: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.geodeticDatum = fix_values.hallucinated_str(self.geodeticDatum, text)
