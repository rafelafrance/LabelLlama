from typing import Any

from llama.llm.herbarium_sheet import HerbariumSheet

SIGNATURE_REGISTRY: dict[str, Any] = {
    "herbarium": HerbariumSheet,
}
