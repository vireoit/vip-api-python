import requests
from flask import request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import Response as flask_response
from flask import make_response
from app.response import Response
from app.status_constants import HttpStatusCode
from app.subjects.delegates import SubjectDelegate
import json


api = Namespace("VIP", description="Namespace for VIP API Services")


@api.route("/subject/export")
class SubjectExport(Resource):
    """
    Class for export files
    """
    # @jwt_required()
    def post(self):
        """
        Return all subjects
        """
        claims = ""

        payload = request.json
        data = {

            'export_fields': payload['export_fields'] if 'export_fields' in payload else [],
        }
        SubjectDelegate.export_subjects(filters=data,user_identity=claims)
        resp = make_response('subjects.xls')
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=subjects.xls'
        return resp


@api.route("/subject/pain")
class SubjectExport(Resource):
    """
    Class for export files
    """
    # @jwt_required()
    def get(self):
        """
        Return all subjects
        """
        claims = ""
        parameters = {
            'subject': "",
            'date': "",
        }

        if 'subject' in request.args and request.args.get('subject'):
            parameters['subject'] = request.args.get('subject')
        if 'date' in request.args and request.args.get('date'):
            parameters['date'] = request.args.get('date')

        data = SubjectDelegate.pain_details(filters=parameters, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Company profile and jobs")


