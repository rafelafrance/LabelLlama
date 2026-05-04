from dataclasses import dataclass, field

from llama.fields.base_field import BOTH, BaseField
from llama.pylib import fix_values
from llama.pylib.str_util import compress

STATE_PROVINCE: str = compress("""
    `stateProvince` (str):
    Extract the state, province, or equivalent first-level administrative division
    where the specimen was collected (e.g., 'California', 'Ontario', 'Coahuila').
    Return the full name, not an abbreviation or acronym.
    If the state/province is not stated but can be inferred from the locality,
    return the inferred value.
    If no state/province information is available, return an empty string.
    """)


@dataclass
class StateProvince(BaseField):
    stateProvince: str = field(default="", metadata=BOTH)

    def __post_init__(self, text: str) -> None:
        self.stateProvince = fix_values.hallucinated_str(self.stateProvince, text)
