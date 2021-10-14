from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from flask import Response as flask_response
from flask import make_response
from app.response import Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_constants import HttpStatusCode
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
# from app import constants
from app.home.delegates import PegScoreDelegate
from flask_restx import Api, Resource, fields

api = Namespace("Home", description="Namespace for Home")


@api.route("/home/peg", defaults={'id': None})
@api.route("/home/peg/<id>")
class CreatePegDetails(Resource):
    """
    Class for export files
    """
    # @jwt_required()
    def post(self, id):
        """
        Create peg score of subjects
        """
        claims = ""
        payload = request.json
        data = PegScoreDelegate.create_peg_score_record(payload, user_identity=claims)
        return Response.success(response_data={},
                                status_code=HttpStatusCode.OK, message="Peg score Successfully created")

    # @jwt_required()
    def get(self, id):
        """
        Return all subjects
        """
        claims = ""
        parameters = {
            'subject': ""
        }

        if 'subject' in request.args and request.args.get('subject'):
            parameters['subject'] = request.args.get('subject')

        data = PegScoreDelegate.peg_score_details(filters=parameters, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Peg score details")

