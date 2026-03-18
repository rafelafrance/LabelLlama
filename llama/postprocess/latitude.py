from llama.postprocess.base_action import BaseAction, FieldData


class Latitude(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.input_name]
        field_data.output_field[self.input_name] = field
