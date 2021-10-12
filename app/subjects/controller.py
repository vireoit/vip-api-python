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
class MetaData(Resource):
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
        resp = make_response('subjects.xls')
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=subjects.xls'
        return resp

        # return Response.success(response_data={},
        #                         status_code=HttpStatusCode.OK,
        #                         message="subjects")

