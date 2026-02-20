from typing import Any

from llama.signatures.cas_v1 import CasV1
from llama.signatures.herbarium_sheet import HerbariumSheet

SIGNATURES: dict[str, Any] = {
    "herbarium": HerbariumSheet,
    "cas_v1": CasV1,
}
