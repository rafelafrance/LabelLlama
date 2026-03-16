import re
from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class County(FieldAction):
    def postprocess(self, subfields: dict[str, Any], _doc_text: str) -> dict[str, Any]:
        county = subfields["county"]
        county = re.sub(r"\s(co\.?|county)$", "", county, flags=re.IGNORECASE)

        rec = {"county": county.title()}

        postprocess.clean_empties(rec)
        return rec
