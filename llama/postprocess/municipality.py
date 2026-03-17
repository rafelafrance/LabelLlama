from llama.postprocess.field_action import FieldAction, FieldData


class Municipality(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.verbatim]
        field_data.new[self.verbatim] = field.title()