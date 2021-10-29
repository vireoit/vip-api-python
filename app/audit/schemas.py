from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from app.audit.constants import AuditLogEvents


class CreateAuditLog(ma.Schema):

    module = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])
    data = fields.Dict(required=True)
    action = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])
    event = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])

    @validates_schema(skip_on_field_errors=False)
    def validate_object(self, data, **kwargs):
        if 'data' not in data:
            raise ValidationError("Field required", field_name='data')
        if data.get("data") and len(data['data']) < 1:
            raise ValidationError("Field required", field_name='data')

        module = data.get("module")
        event = data.get("event")

        logs = AuditLogEvents.LOGS
        listed_logs = list()
        listed_logs.append(logs["admin_log"]["name"])
        listed_logs.append(logs["user_log"]["name"])
        admin_events = logs["admin_log"]["events"]
        user_events = logs["user_log"]["events"]

        if module not in listed_logs:
            raise ValidationError("Invalid module", field_name='module')

        if str(module) == str(logs["admin_log"]["name"]) and event not in admin_events:
            raise ValidationError("Invalid event", field_name='event')

        elif module == logs["user_log"]["name"] and event not in user_events:
            raise ValidationError("Invalid event", field_name='event')
