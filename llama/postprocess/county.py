import re

from llama.postprocess.base_action import BaseAction, FieldData


class County(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.output_name]
        field = re.sub(r"\s(co\.?|county)$", "", field, flags=re.IGNORECASE)
        field_data.output_field[self.output_name] = field
