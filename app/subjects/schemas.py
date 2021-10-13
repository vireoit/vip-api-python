from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from datetime import date, datetime


class SubjectImportSchema(ma.Schema):
    subjects = fields.List(fields.Dict, required=True)

    @validates_schema(skip_on_field_errors=False)
    def validate_object(self, data, **kwargs):
        subjects = data.get('subjects')
        for data_dict in subjects:
            email = data_dict.get('Email')
            phone = data_dict.get('Phone')
            if not email:
                raise ValidationError("Email is mandatory", field_name="Email")
            if not phone:
                raise ValidationError("Phone is mandatory", field_name="Phone")
