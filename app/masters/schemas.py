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


class MedicationImportSchema(ma.Schema):
    medication = fields.List(fields.Dict, required=True)

    @validates_schema(skip_on_field_errors=False)
    def validate_object(self, data, **kwargs):
        medication = data.get('medication')
        for data_dict in medication:
            name = data_dict.get('MedicationName')
            amount = data_dict.get('Amount')
            is_vireo_product = data_dict.get('ProductType')
            if name is None and is_vireo_product is None:
                raise ValidationError("Medication Name and IsVireoProduct field should not be empty", field_name="Medication Name")
            if not name:
                raise ValidationError("Medication Name is mandatory", field_name="Medication Name")
            if not is_vireo_product:
                raise ValidationError("Product Type number is mandatory", field_name="Product Type")
