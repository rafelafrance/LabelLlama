from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

SCIENTIFIC_NAME_AUTHORSHIP: str = compress("""
    Scientific name authorship.
    There is often more than one author per scientific name.
    Authors may be abbreviated, sometimes as a single letter.
    """)


@dataclass
class ScientificNameAuthorship(BaseField):
    scientificNameAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        values = fix_values.to_list_of_strs(self.scientificNameAuthorship)
        values = [v.title() for v in values]
        self.scientificNameAuthorship = fix_values.reduce_str_list(values)


DEFAULTS = DotDict({f.name: f.default for f in fields(ScientificNameAuthorship)})
