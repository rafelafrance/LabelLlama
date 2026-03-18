from llama.postprocess.base_action import BaseAction, FieldData


class InfraspecificEpithet(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.output_name]
        field_data.output_field[self.output_name] = field.title()
