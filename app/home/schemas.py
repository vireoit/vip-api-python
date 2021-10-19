from app import ma, subjects
from marshmallow import post_load, fields, validate, validates,ValidationError,validates_schema
from datetime import date, datetime


class QuestionAnswer(ma.Schema):
    Question = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])
    value = fields.Integer(required=True)


class PegScore(ma.Schema):
    SubjectId = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])
    QuestionAnswers = fields.List(fields.Nested(QuestionAnswer, required=True))

    @validates_schema(skip_on_field_errors=False)
    def validate_object(self, data, **kwargs):
        if 'QuestionAnswers' in data:
            if len(data['QuestionAnswers']) < 1:
                raise ValidationError("Field required", field_name='QuestionAnswers')


class FeedBack(ma.Schema):
    SubjectId = fields.String(required=True, validate=[validate.Length(min=1, error="Field Required")])
    feedback = fields.String(required=True, validate=[validate.Length(min=1, max=1000, error="Field Required")])





