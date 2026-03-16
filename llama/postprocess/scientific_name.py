from typing import Any

from llama.postprocess.field_action import FieldAction


class ScientificName(FieldAction):
    def postprocess(self, subfields: dict[str, Any], _doc_text: str) -> dict[str, Any]:
        genus, species, *_ = subfields["scientificName"].split()
        return {"scientificName":  f"{genus.title()} {species.lower()}"}
