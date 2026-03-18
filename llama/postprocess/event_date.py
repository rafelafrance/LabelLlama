from calendar import IllegalMonthError

from dateutil import parser

from llama.postprocess.base_action import BaseAction, FieldData


class EventDate(BaseAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.output_field["eventDate"]

        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("date")]
            field = " ".join(field)

        try:
            date_ = parser.parse(field).date()
            date_ = date_.isoformat()[:10]
        except parser.ParserError, IllegalMonthError:
            date_ = ""

        field_data.output_field["verbatimEventDate"] = field
        field_data.output_field["eventDate"] = date_
