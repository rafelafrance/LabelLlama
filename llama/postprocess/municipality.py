from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class Municipality(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        field = subfields["municipality"]
        rec = {"municipality": field.title()}
        postprocess.clean_empties(rec)
        return rec
