import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, HIDE, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

COLLECTOR: str = compress("""
    Extract the name of the person or people who collected the specimen.
    The collector name may appear with labels like 'col.', 'coll.', 'coll. by',
    or 'collected by'. Multiple collectors may be separated by '&', 'and',
    or commas.
    Preserve the name as written — do not expand abbreviations.
    If no collector is named, return the default value.
    """)


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
