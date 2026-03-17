from llama.postprocess.field_action import FieldAction, FieldData

# from dateutil import parser
# from calendar import IllegalMonthError


class DateIdentified(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new[self.name]
        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("date")]
            field = " ".join(field)

        # try:
        #     date_ = parser.parse(field).date()
        #     date_ = date_.isoformat()[:10]
        # except parser.ParserError, IllegalMonthError:
        #     date_ = ""

        field_data.new[self.name] = field

