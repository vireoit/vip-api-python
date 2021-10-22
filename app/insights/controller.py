from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from flask import Response as flask_response
from flask import make_response
from app.response import Response
from flask_jwt_extended import get_jwt_identity
from app.flask_jwt import jwt_required
from app.status_constants import HttpStatusCode
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
from app.insights.delegates import InsightDelegate
# from app import constants

from flask_restx import Api, Resource, fields

api = Namespace("Insights", description="Namespace for Insights")

@api.route("/insights/personal/export")
class InsightsPersonalExport(Resource):
    """
    Class for export files
    """
    @jwt_required()
    def post(self):
        claims = {"authorization": request.headers.get('Authorization')}
        payload = request.json
        InsightDelegate.export_personal_insights(parameters=payload, user_identity=claims)
        resp = make_response('Insight-Personal-export.xls')
        resp.data = open("Insight-Personal-export.xls", "rb").read()
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=Insight-Personal-export.xls'
        return resp

@api.route("/insights/community/export")
class InsightsPersonalExport(Resource):
    """
    Class for export files
    """
    @jwt_required()
    def post(self):
        claims = {"authorization": request.headers.get('Authorization')}
        payload = request.json
        InsightDelegate.export_community_insights(parameters=payload, user_identity=claims)
        resp = make_response('Insight-Community-export.xls')
        resp.data = open("Insight-Community-export.xls", "rb").read()
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=Insight-Community-export.xls'
        return resp