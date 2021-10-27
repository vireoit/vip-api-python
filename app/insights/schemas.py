from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from datetime import date, datetime


class EventSchema(ma.Schema):
    EventType = fields.List(fields.String(required=True))
    StartDate = fields.Date(required=True)
    IsOngoing = fields.Boolean(required=True)
    IsCannabisProduct = fields.String(required=False, allow_none=True)
    TreatmentInfo = fields.String(required=False, allow_none=True)
    SubjectId = fields.String(required=True)

    @validates_schema(skip_on_field_errors=True)
    def validate_object(self, data, **kwargs):
        EventType = data.get('EventType')
        if len(EventType) < 0:
            raise ValidationError("Event Type can not be empty", field_name="EventType")
        if data['StartDate'] > date.today():
            raise ValidationError("Future date not allowed", field_name="StartDate")