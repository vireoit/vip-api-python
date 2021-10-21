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
from app.home.schemas import PegScore, FeedBack, Satisfaction
# from app import constants
from app.home.delegates import PegScoreDelegate, OnGoingFeedBack, SatisfactionDelegate
from flask_restx import Api, Resource, fields

api = Namespace("Home", description="Namespace for Home")


@api.route("/home/peg", defaults={'id': None})
@api.route("/home/peg/<id>")
class CreatePegDetails(Resource):
    """
    Class for export files
    """
    @jwt_required()
    def post(self, id):
        """
        Create peg score of subjects
        """
        try:
            claims = ""
            payload = request.json
            PegScore().load(payload)
            data = PegScoreDelegate.create_peg_score_record(payload, user_identity=claims)
            return Response.success(response_data={},
                                    status_code=HttpStatusCode.OK, message="Peg score Successfully created")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message="Validation Error Occurred")

    @jwt_required()
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


@api.route("/home/feedback")
@api.doc(paylod={'subject': 'ID of the Subject - 60bb10c89cf5432080d40346 ', "feedback": "give your feed back"})
class OnGoingFeedback(Resource):
    """
    Class for export files
    """
    @jwt_required()
    def post(self):
        """
        Create peg score of subjects
        """
        try:
            claims = ""
            payload = request.json
            FeedBack().load(payload)
            data = OnGoingFeedBack.create_on_going_feedback(payload, user_identity=claims)
            return Response.success(response_data={},
                                    status_code=HttpStatusCode.OK, message="Feedback Successfully created")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message="Validation Error Occurred")


@api.route("/home/satisfaction", defaults={'id': None})
@api.route("/home/satisfaction/<id>")
class CreateSatisfactionDetails(Resource):
    """
    Class for export files
    """
    # @jwt_required()
    def post(self, id):
        """
        Create peg score of subjects
        """
        try:
            claims = ""
            payload = request.json
            Satisfaction().load(payload)
            data = SatisfactionDelegate.create_satisfaction_score_record(payload, user_identity=claims)
            return Response.success(response_data={},
                                    status_code=HttpStatusCode.OK, message="Satisfaction score Successfully created")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message="Validation Error Occurred")

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

        data = SatisfactionDelegate.satisfaction_score_details(filters=parameters, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Satisfaction score details")