import re
from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

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
