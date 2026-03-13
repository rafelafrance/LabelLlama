from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class Family(FieldAction):
    def preprocess(self, text: str, ocr_text: str) -> str:
        return text if text in ocr_text else ""

    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        subfields["family"] = subfields["family"].title()
        postprocess.clean_empties(subfields)
        return subfields
