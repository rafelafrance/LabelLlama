from llama.postprocess.field_action import FieldAction, FieldData


class ScientificName(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        genus, species, *_ = field_data.new[self.name].split()
        field_data.new[self.name].text = f"{genus.title()} {species.lower()}"
