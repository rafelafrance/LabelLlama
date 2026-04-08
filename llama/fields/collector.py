import re
from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, HIDE, BaseField

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


DEFAULTS = {f.name: f.default for f in fields(Collector)}
