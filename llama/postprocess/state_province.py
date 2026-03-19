from llama.common import fix_values
from llama.postprocess.base_action import BaseAction, FieldData


class StateProvince(BaseAction):
    def preprocess_field(self, field_data: FieldData) -> None:
        field_value = field_data.input_field[self.input_name]
        field_data.output_field[self.output_name] = fix_values.to_str(field_value)


