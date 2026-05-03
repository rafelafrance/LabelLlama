import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, HIDE, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

COLLECTOR: str = compress("""The person or people who collected the specimen.""")


@dataclass
class Collector(BaseField):
    collector: str = field(default="", metadata=BOTH | HIDE)
    recordedBy: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.collector = fix_values.to_str(self.collector)

        # Remove the collector label
        self.collector = re.sub(r"^col\w*[.:,;]?\s+", "", self.collector)

        self.recordedBy = self.collector
