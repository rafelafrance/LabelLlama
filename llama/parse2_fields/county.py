import re
from typing import Any

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class County(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        field = subfields["county"]
        field = re.sub(r"\s(co\.?|county)$", "", field, flags=re.IGNORECASE)

        rec = {"county": field.title()}

        postprocess.clean_empties(rec)
        return rec
