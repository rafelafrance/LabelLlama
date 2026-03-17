from llama.postprocess.field_action import FieldAction, FieldData


class Family(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.name]
        if field in field_data.old["doc_text"]:
            field_data.new[self.name] = field.title()
