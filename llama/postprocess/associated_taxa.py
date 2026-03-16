from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class AssociatedTaxa(FieldAction):
    def postprocess(self, subfields: dict[str, Any], _doc_text: str) -> dict[str, Any]:
        taxa = subfields["associatedTaxa"]
        taxa = taxa.replace("*", "")
        taxa = taxa.removesuffix(".")
        rec = {"associatedTaxa": taxa}
        postprocess.clean_empties(rec)
        return rec
