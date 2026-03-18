from llama.postprocess.base_action import BaseAction, FieldData


class Family(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.output_name]
        if field in field_data.input_field["doc_text"]:
            field_data.output_field[self.output_name] = field.title()
