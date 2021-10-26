from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from datetime import date, datetime


class RewardSchema(ma.Schema):
    reward_configuration = fields.List(fields.Dict, required=True)

    @validates_schema(skip_on_field_errors=False)
    def validate_object(self, data, **kwargs):
        reward = data.get('reward_configuration')

        for data_dict in reward:
            event_type = data_dict.get('eventType')
            action = data_dict.get('action')
            points = data_dict.get('points')

            if event_type is None or event_type == "" and action is None or action == "":
                raise ValidationError("Event type and action required", field_name="eventType, action")
            if event_type is None or event_type == "":
                raise ValidationError("Event type is mandatory", field_name="eventType")
            if action is None or action == "":
                raise ValidationError("Action is mandatory", field_name="action")
