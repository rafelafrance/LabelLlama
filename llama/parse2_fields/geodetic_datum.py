from typing import Any

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class GeodeticDatum(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        subfields["geodeticDatum"] = subfields["geodeticDatum"].upper()
        postprocess.clean_empties(subfields)
        return subfields
