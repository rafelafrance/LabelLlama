from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class InfraspecificNameAuthorship(BaseField):
    infraspecificNameAuthorship: list[str] | str | None = field(
        default="", metadata=BOTH
    )

    def __post_init__(self, text: str) -> None:
        del text

        values = fix_values.to_list_of_strs(self.infraspecificNameAuthorship)
        values = [v.title() for v in values]
        self.infraspecificNameAuthorship = fix_values.reduce_list(values)
