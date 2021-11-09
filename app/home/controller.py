from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from flask import Response as flask_response
from flask import make_response
from app.response import Response
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.flask_jwt import jwt_required
from app.status_constants import HttpStatusCode
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
from app.home.schemas import PegScore, FeedBack, Satisfaction
# from app import constants
from app.home.delegates import PegScoreDelegate, OnGoingFeedBack, SatisfactionDelegate, AdminHomeDelegate
from app.home.delegates import PegScoreDelegate, OnGoingFeedBack, SatisfactionDelegate, RewardRedemption
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
            claims = get_jwt()
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
        claims = get_jwt()
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
            claims = get_jwt()
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
    @jwt_required()
    def post(self, id):
        """
        Create peg score of subjects
        """
        try:
            claims = get_jwt()
            payload = request.json
            Satisfaction().load(payload)
            data = SatisfactionDelegate.create_satisfaction_score_record(payload, user_identity=claims)
            return Response.success(response_data={},
                                    status_code=HttpStatusCode.OK, message="Satisfaction score Successfully created")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message="Validation Error Occurred")

    @jwt_required()
    def get(self, id):
        """
        Return all subjects
        """
        claims = get_jwt()
        parameters = {
            'subject': ""
        }

        if 'subject' in request.args and request.args.get('subject'):
            parameters['subject'] = request.args.get('subject')

        data = SatisfactionDelegate.satisfaction_score_details(filters=parameters, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Satisfaction score details")


@api.route("/home/admin/statistics")
class AdminHomeStatistics(Resource):
    @jwt_required()
    def get(self):
        parameters = {}
        data = AdminHomeDelegate.get_admin_home_statistics(parameters=parameters)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Admin home statistics fetched successsfully")

@api.route("/home/admin/patients")
@api.doc(paylod={'frequency': 'Today/Weekly/Monthly'})
class AdminHomePatientsGraph(Resource):
    @jwt_required()
    def get(self):
        parameters = {
            "frequency": request.args.get("frequency")
        }
        data = AdminHomeDelegate.get_admin_home_patients(parameters=parameters)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Graph Details for patients fetched successsfully")

@api.route("/home/admin/treatments")
@api.doc(paylod={'frequency': 'Today/Weekly/Monthly'})
class AdminHomeTreatmentsGraph(Resource):
    @jwt_required()
    def get(self):
        claims = {"authorization": request.headers.get('Authorization'), "subject_id": get_jwt_identity()}
        parameters = {
            "frequency": request.args.get("frequency")
        }
        data = AdminHomeDelegate.get_admin_home_treatments(parameters=parameters, claims=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Graph Details for treatments fetched successsfully")

@api.route("/home/admin/surveys")
@api.doc(paylod={'frequency': 'Today/Weekly/Monthly'})
class AdminHomeSurveysGraph(Resource):
    @jwt_required()
    def get(self):
        parameters = {
            "frequency": request.args.get("frequency")
        }
        data = AdminHomeDelegate.get_admin_home_surveys(parameters=parameters)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Graph Details for surveys fetched successsfully")

@api.route("/home/admin/pain_type")
@api.doc(paylod={'frequency': 'Today/Weekly/Monthly'})
class AdminHomePainTypeGraph(Resource):
    @jwt_required()
    def get(self):
        claims = {"authorization": request.headers.get('Authorization'), "subject_id": get_jwt_identity()}
        parameters = {
            "frequency": request.args.get("frequency")
        }
        data = AdminHomeDelegate.get_admin_home_pain_type(parameters=parameters, claims=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Graph Details for pain type fetched successsfully")

@api.route("/home/rewards")
@api.doc(payload={'subject': 'Subject IDs- 60bb10c89cf5432080d40346 ', "frequency": "today, week, month"})
class ListRewards(Resource):
    """
    Class for list rewards
    """
    @jwt_required()
    def get(self):
        """
        Return all rewards
        """
        claims = ""
        parameters = {
            "subject": request.args.get("subject"),
            "frequency": request.args.get("param")
        }

        data = RewardRedemption.list_accumulated_rewards(filters=parameters, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="List of rewards")

