from llama.postprocess.field_action import FieldAction, FieldData


class RecordNumber(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.name]
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("no")]
            field = " ".join(field)
        field_data.new[self.name] = field
