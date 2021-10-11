import requests
from flask import request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import Response as flask_response
from app.response import Response
from app.status_constants import HttpStatusCode
from app.subjects.delegates import SubjectDelegate
import json

api = Namespace("VIP", description="Namespace for VIP API Services")


@api.route("/subject/export")
class MetaData(Resource):
    """
    Class for export files
    """
    def post(self):
        """
        Return all subjects
        """
        claims = get_jwt()

        payload = request.json
        data = {

            'export_fields': payload['export_fields'] if 'export_fields' in payload else [],
        }
        program = SubjectDelegate.export_subjects(filters=data, user_identity=claims)
        return Response.success(response_data={},
                                status_code=HttpStatusCode.OK,
                                message="subjects")

