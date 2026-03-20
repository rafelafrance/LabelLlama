from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class InfraspecificNameAuthorship(BaseField):
    infraspecificNameAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self) -> None:
        self.infraspecificNameAuthorship = fix_values.to_str(
            self.infraspecificNameAuthorship
        ).title()
