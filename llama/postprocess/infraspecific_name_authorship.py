from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class InfraspecificNameAuthorship(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        field = subfields["infraspecificNameAuthorship"]
        rec = {"infraspecificNameAuthorship": field.title()}
        postprocess.clean_empties(rec)
        return rec
