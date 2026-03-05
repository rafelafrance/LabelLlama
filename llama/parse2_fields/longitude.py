from typing import Any

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class Longitude(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        postprocess.clean_empties(subfields)
        return subfields
