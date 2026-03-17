from llama.postprocess.field_action import FieldAction, FieldData


class AssociatedTaxa(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.name]
        field = field.replace("*", "")
        field = field.removesuffix(".")
        field_data.new[self.name] = field
