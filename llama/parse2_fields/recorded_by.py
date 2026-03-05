from typing import Any

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class RecordedBy(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        field = subfields["recordedBy"]
        rec = {"recordedBy": field.title()}
        postprocess.clean_empties(rec)
        return rec
