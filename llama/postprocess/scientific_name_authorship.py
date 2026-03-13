from typing import Any

from llama.postprocess import postprocess
from llama.postprocess.field_action import FieldAction


class ScientificNameAuthorship(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        postprocess.clean_empties(subfields)
        return subfields
