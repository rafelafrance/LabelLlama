from typing import Any

from llama.parse2_fields import postprocess
from llama.parse2_fields.field_action import FieldAction


class Habitat(FieldAction):
    def postprocess(self, subfields: dict[str, Any], text: str) -> dict[str, Any]:
        habitat = subfields["habitat"]
        if habitat:
            habitat = habitat.split()
            habitat = [s for s in habitat if not s.lower().startswith("habitat")]
            habitat = " ".join(habitat)

        rec = {"habitat": habitat}
        postprocess.clean_empties(rec)
        return rec
