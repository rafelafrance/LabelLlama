from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class GeodeticDatum(FieldAction):
    def postprocess(self, subfields: dict[str, Any], _doc_text: str) -> dict[str, Any]:
        subfields["geodeticDatum"] = subfields["geodeticDatum"].upper()
        postprocess.clean_empties(subfields)
        return subfields
