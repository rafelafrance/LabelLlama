from typing import Any

from llama.parse2_fields.field_action import FieldAction


class ScientificName(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        genus, species, *_ = subfields["scientificName"].split()
        return {"scientificName":  f"{genus.title()} {species.lower()}"}
