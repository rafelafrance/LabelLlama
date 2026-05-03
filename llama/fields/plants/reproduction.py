from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

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
        self.reproduction = fix_values.hallucinated_str(self.reproduction, text)
