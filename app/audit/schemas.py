from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema


class CreateAuditLog(ma.Schema):
    module = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])
    data = fields.Dict(required=True)
    action = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])

    @validates_schema(skip_on_field_errors=False)
    def validate_object(self, data, **kwargs):
        if 'data' not in data:
            raise ValidationError("Field required", field_name='data')
        if data.get("data") and len(data['data']) < 1:
            raise ValidationError("Field required", field_name='data')
