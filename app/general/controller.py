import requests
from flask import request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import Response as flask_response
from app.response import Response
from app.status_constants import HttpStatusCode
from app.general.delegates import  TestEmailDelegate

api = Namespace("General", description="Namespace for general")


@api.route("/test-email")
class CreatePegDetails(Resource):
    """
    Class for export files
    """
    # @jwt_required()
    def get(self):
        """
        Create peg score of subjects
        """
        data = TestEmailDelegate.test_email()
        return Response.success(response_data={},
                                status_code=HttpStatusCode.OK, message=" Successfully")

