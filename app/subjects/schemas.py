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
            name = data_dict.get('Name')
            address = data_dict.get('Address')
            gender = data_dict.get('Gender')
            city = data_dict.get('City')
            state_name = data_dict.get('StateName')
            postal = data_dict.get('PostalCode')
            state_code = data_dict.get('StateCode')
            if name is None or name == "nan":
                raise ValidationError("Mandatory fields missing", field_name="Name")
            if address is None or address == "nan":
                raise ValidationError("Mandatory fields missing", field_name="Address")
            if gender is None or gender == "nan":
                raise ValidationError("Mandatory fields missing", field_name="Gender")
            if city is None or city == "nan":
                raise ValidationError("Mandatory fields missing", field_name="City")
            if state_name is None or state_name == "nan":
                raise ValidationError("Mandatory fields missing", field_name="State Name")
            if postal is None or postal == "nan":
                raise ValidationError("Mandatory fields missing", field_name="Postal")
            if state_code is None or state_code == "nan":
                raise ValidationError("Mandatory fields missing", field_name="State Code")
            if phone == "nan" or phone is None:
                raise ValidationError("Mandatory fields missing", field_name="Phone")
            if email == "nan" or email is None:
                raise ValidationError("Mandatory fields missing", field_name="Email")
        
