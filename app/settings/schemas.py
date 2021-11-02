from dns.resolver import reset_default_resolver
from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from datetime import date, datetime
import validators

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

class ResourceConfigurationSchema(ma.Schema):
    resource_title = fields.String(required=True, validate=[validate.Length(min=1, error="Resource title should not be empty")])
    description = fields.String(required=False)
    link = fields.String(required=True, validate=[validate.Length(min=1, error="Link should not be empty")])


    @validates_schema(skip_on_field_errors=True)
    def validate_object(self, data, **kwargs):
        resource_title = data.get('resource_title')
        description = data.get('description')
        link = data.get('link')
        if resource_title is None:
            raise ValidationError("Resource Title should not be empty", field_name="Resources")
        if len(resource_title) > 50:
            raise ValidationError("Resource Title can contain maximum of 50 characters", field_name="Resources")
        if description and len(description) > 500:
            raise ValidationError("Limit exceeds", field_name="Resources")
        is_link_valid = validators.url(link)
        if is_link_valid != True:
            raise ValidationError("Please add a valid link", field_name="Resources")
