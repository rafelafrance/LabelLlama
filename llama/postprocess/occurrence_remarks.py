from dataclasses import dataclass, field

from llama.common import fix_values
from llama.postprocess.base_field import BOTH, BaseField


@dataclass
class OccurrenceRemarks(BaseField):
    occurrenceRemarks: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.occurrenceRemarks = fix_values.to_str(self.occurrenceRemarks)
