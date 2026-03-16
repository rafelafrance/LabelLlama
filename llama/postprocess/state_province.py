from typing import Any

from llama.postprocess.field_action import FieldAction


class StateProvince(FieldAction):
    def postprocess(self, subfields: dict[str, Any], doc_text: str) -> dict[str, Any]:
        state = subfields["stateProvince"]
        return state if state in doc_text else ""
