from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class EventDate(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        field = subfields["eventDate"]
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("date")]
            field = " ".join(field)

        rec = {"verbatimEventDate": field}
        postprocess.clean_empties(rec)
        return rec
