from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from flask import Response as flask_response
from flask import make_response
from app.response import Response
from app.flask_jwt import jwt_required
from app.status_constants import HttpStatusCode
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
# from app import constants
from app.surveys.delegates import SurveyDelegate
import json

api = Namespace("Surveys", description="Namespace for Survey report export")


@api.route("/survey/export")
@api.doc(params={'survey_id': 'ID of the Survey', 'subject_ids': 'List of subject ids', 'question_list':'List of questions'})
class SurveyReportExport(Resource):
    """
    Class for export survey report
    """
    @jwt_required()
    def post(self):
        payload = request.json
        parameters = {"authorization": request.headers.get('Authorization')}
        data = {
            'survey_id': payload['survey_id'] if 'survey_id' in payload else " ",
            'subject_ids': payload['subject_ids'] if 'subject_ids' in payload else [],
            'question_list': payload['question_list'] if 'question_list' in payload else []
        }
        SurveyDelegate.export_survey_reports(filters=data, parameters=parameters)
        resp = make_response('survey_reports.xls')
        resp.data = open("survey_reports.xls", "rb").read()
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=survey_reports.xls'
        return resp

