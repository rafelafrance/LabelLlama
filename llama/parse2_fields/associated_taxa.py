from typing import Any

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class AssociatedTaxa(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        taxa = subfields["associatedTaxa"]
        taxa = taxa.replace("*", "")
        taxa = taxa.removesuffix(".")
        rec = {"associatedTaxa": taxa}
        postprocess.clean_empties(rec)
        return rec
