from dataclasses import dataclass, field, fields

from llama.common import fix_values
from llama.common.dot_dict import DotDict
from llama.common.str_util import compress
from llama.fields.base_field import BOTH, BaseField

PLANT_REPRODUCTION: str = compress("""
    What is the plant's habit?
    Examples: "androdioecious", "androecious", "androgynomonoecious", "androgynous",
    "andromonoecious", "dichogamous", "dioecious", "gynodioecious", "gynodioecy",
    "gynoecious", "gynomonoecious", "hermaphrodite", "hermaphrodite", "monoecious",
    "polygamodioecious", "polygamomonoecious", "polygamous", "protogynous",
    "subandroecious", "subdioecious", "subgynoecious", "trimonoecious", "trioecious".
    """)


@dataclass
class Reproduction(BaseField):
    reproduction: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        del text

        self.reproduction = fix_values.to_str(self.reproduction)


DEFAULTS = DotDict({f.name: f.default for f in fields(Reproduction)})
