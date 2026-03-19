from llama.common import fix_values
from llama.postprocess.base_action import BaseAction, FieldData


class Habitat(BaseAction):
    def preprocess_field(self, field_data: FieldData) -> None:
        field_value = field_data.input_field[self.input_name]
        field_data.output_field[self.output_name] = fix_values.to_str(field_value)

    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.output_name]
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("habitat")]
            field = " ".join(field)
        field_data.output_field[self.output_name] = field
