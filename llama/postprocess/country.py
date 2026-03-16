from typing import Any

from llama.postprocess.field_action import FieldAction


class Country(FieldAction):
    def postprocess(self, subfields: dict[str, Any], doc_text: str) -> dict[str, Any]:
        country = subfields["country"]
        return country if country in doc_text else ""
