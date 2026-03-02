from typing import Any

from llama.parse1_text.cas_v1 import CasV1
from llama.parse1_text.herbarium_sheet import HerbariumSheet

SIGNATURES: dict[str, Any] = {
    "herbarium": HerbariumSheet,
    "cas_v1": CasV1,
}
