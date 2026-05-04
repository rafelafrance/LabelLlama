from typing import Any

from llama.llm.herbarium_sheet import HerbariumSheet
from llama.llm.insect_label import InsectLabel

SIGNATURE_REGISTRY: dict[str, Any] = {
    "herbarium": HerbariumSheet,
    "insect": InsectLabel,
}
