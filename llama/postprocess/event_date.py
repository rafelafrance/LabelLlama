from calendar import IllegalMonthError

from dateutil import parser

from llama.postprocess.field_action import FieldAction, FieldData


class EventDate(FieldAction):
    def postprocess(self, field_data: FieldData) -> None:
        field = field_data.new["eventDate"]

        if field:
            field = field.split()
            field = [s for s in field if not s.lower().startswith("date")]
            field = " ".join(field)

        try:
            date_ = parser.parse(field).date()
            date_ = date_.isoformat()[:10]
        except parser.ParserError, IllegalMonthError:
            date_ = ""

        field_data.new["verbatimEventDate"] = field
        field_data.new["eventDate"] = date_
