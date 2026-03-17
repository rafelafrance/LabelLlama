from llama.postprocess.field_action import FieldAction, FieldData


class InfraspecificEpithet(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.name]
        field_data.new[self.name] = field.title()
