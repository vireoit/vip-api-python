from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from datetime import date, datetime


class MasterEventSchema(ma.Schema):
    event_type = fields.String(required=True, validate=[validate.Length(min=1, error="Event Type should not be empty")])
    instruction = fields.String(required=False)

    @validates_schema(skip_on_field_errors=True)
    def validate_object(self, data, **kwargs):
        event_type = data.get('event_type')
        if event_type is None:
            raise ValidationError("Event Type should not be empty", field_name="Event")
        if len(event_type) > 1000:
            raise ValidationError("Event Type can contain maximum of 1000 characters", field_name="Event")

