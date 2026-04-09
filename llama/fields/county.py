import re
from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

COUNTY: str = compress("""The county where the specimen was collected.""")


@dataclass
class County(BaseField):
    county: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.county = fix_values.to_str(self.county)

        # Remove the county label
        self.county = re.sub(r"\s(co\.?|county)$", "", self.county, flags=re.IGNORECASE)

        self.county = self.county.title()


DEFAULTS = DotDict({f.name: f.default for f in fields(County)})
