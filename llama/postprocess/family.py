from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class Family(FieldAction):
    def postprocess(self, subfields: dict[str, Any], doc_text: str) -> dict[str, Any]:
        if subfields["family"] not in doc_text:
            return subfields
        subfields["family"] = subfields["family"].title()
        postprocess.clean_empties(subfields)
        return subfields
