from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

SCIENTIFIC_NAME_AUTHORSHIP: str = compress("""
    `scientificNameAuthorship` (str):
    Extract the authorship citation for the species-level scientific name.
    This is the person(s) who originally described the species, e.g., 'L.',
    'Smith & Jones', '(Bartlett) Fernald'. There may be multiple authors.
    Authors are often abbreviated, sometimes to a single letter.
    This author may include a publication year, include that.
    Do not include infraspecific authorship — that has its own field.
    If no authorship is stated, return an empty string.
    """)


@dataclass
class ScientificNameAuthorship(BaseField):
    scientificNameAuthorship: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text
        self.scientificNameAuthorship = fix_values.to_str(self.scientificNameAuthorship)
        self.scientificNameAuthorship = fix_values.clean_str_ends(
            self.scientificNameAuthorship
        )
