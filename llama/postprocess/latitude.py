from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class Latitude(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        rec = {"verbatimLatitude": subfields["latitude"]}
        postprocess.clean_empties(rec)
        return rec
