from typing import Any

from llama.lm.herbarium_sheet import HerbariumSheet

SIGNATURE_REGISTRY: dict[str, Any] = {
    "herbarium": HerbariumSheet,
}
