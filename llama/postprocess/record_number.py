from llama.postprocess.base_action import BaseAction, FieldData


class RecordNumber(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field[self.output_name]
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("no")]
            field = " ".join(field)
        field_data.output_field[self.output_name] = field
