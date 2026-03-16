from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class DateIdentified(FieldAction):
    def postprocess(self, subfields: dict[str, Any], _doc_text: str) -> dict[str, Any]:
        field = subfields["dateIdentified"]
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("date")]
            field = " ".join(field)

        rec = {"dateIdentified": field}
        postprocess.clean_empties(rec)
        return rec
