from typing import Any

from llama.lm.cas_v1 import CasV1
from llama.lm.herbarium_sheet import HerbariumSheet

SIGNATURES: dict[str, Any] = {
    "cas_v1": CasV1,
    "herbarium": HerbariumSheet,
}
