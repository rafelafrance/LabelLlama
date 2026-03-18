from llama.postprocess.base_action import BaseAction, FieldData


class ScientificName(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        genus, species, *_ = field_data.output_field[self.output_name].split()
        field_data.output_field[self.output_name].text = (
            f"{genus.title()} {species.lower()}"
        )
