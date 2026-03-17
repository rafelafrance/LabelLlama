import re

from llama.postprocess.field_action import FieldAction, FieldData


class County(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.name]
        field = re.sub(r"\s(co\.?|county)$", "", field, flags=re.IGNORECASE)
        field_data.new[self.name] = field