from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from flask import Response as flask_response
from flask import make_response
from app.response import Response
from flask_jwt_extended import  get_jwt_identity, get_jwt
from app.status_constants import HttpStatusCode
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
from app.flask_jwt import jwt_required
# from app import constants
from app.subjects.delegates import SubjectImportDelegate, RatingAndFeedbackDetailsDelegate
from app.subjects.delegates import SubjectDelegate, RewardRedemption, ListAdverseEvent
from flask_restx import Api, Resource, fields


api = Namespace("Subject", description="Namespace for Subject")

export_fields = api.model('ExportFields', {
    'export_fields': fields.List(fields.String)
})


@api.route("/subject/import")
class SubjectImport(Resource):
    @jwt_required()
    def post(self):
        payload = request.files
        parameters = {"authorization": request.headers.get('Authorization')}
        try:
            if 'import_file' in payload:
                file = payload['import_file']
                extension = file.filename.rsplit('.', 1)[1].lower()
                if file.filename == '':
                    raise FileNotSelected(param_name='import_file')
                if file and file_service_util.allowed_document_types(file.filename):
                    if extension == "csv":
                        response = SubjectImportDelegate.import_subject_csv_file(file, parameters)
                    if extension == "xlsx" or extension == "xls":
                        response = SubjectImportDelegate.import_subject_excel_file(file, parameters)
                else:
                    raise FileFormatException(param_name='types are csv/xlsx')
            if response['value'] == True:
                return Response.success(response_data={}, status_code=HttpStatusCode.OK, message=response['message'])
            else:
                if not response['message']:
                    response['message'] = "Subject import failed"
                return Response.error(error_data=response['error_data'], status_code=HttpStatusCode.BAD_REQUEST, 
                    message=response['message'])
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message=list(err.messages.values())[0][0])


@api.route("/subject/export")
@api.doc(params={'export_fields': "array of fields"})
class SubjectExport(Resource):
    """
    Class for export files
    """
    @jwt_required()
    @api.expect(export_fields)
    def post(self):
        """
        Return all subjects
        """
        claims = ""

        payload = request.json
        data = {

            'export_fields': payload['export_fields'] if 'export_fields' in payload else [],
            "from_date": payload['from_date'] if 'from_date' in payload else "",
            "to_date": payload['to_date'] if 'to_date' in payload else "",
            "personal_insights": payload['personal_insights'] if 'personal_insights' in payload else False,
            "user_ratings": payload['user_ratings'] if 'user_ratings' in payload else False,
            "ae_logs": payload['ae_logs'] if 'ae_logs' in payload else False,
            "ae_from_date": payload['ae_from_date'] if 'ae_from_date' in payload else "",
            "ae_to_date": payload['ae_to_date'] if 'ae_to_date' in payload else "",
        }
        SubjectDelegate.export_subjects(filters=data,user_identity=claims)
        resp = make_response('subjects.xls')
        resp.data = open("subjects.xls", "rb").read()
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=subjects.xls'
        return resp


@api.route("/subject/pain")
@api.doc(params={'subject': 'ID of the Subject - 60bb10c89cf5432080d40346 ', "date": "%m-%d-%Y"})
class PainDetails(Resource):
    """
    Class for export files
    """
    @jwt_required()
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
                                status_code=HttpStatusCode.OK, message="Pain Details")


@api.route("/subject/pain/export")
class PainDetailsExport(Resource):
    """
    Class for export files
    """
    @jwt_required()
    def post(self):
        """
        Return all subjects
        """
        claims = ""

        payload = request.json
        data = {

            'subject': payload['subject'] if 'subject' in payload else [],
            "from_date": payload['from_date'] if 'from_date' in payload else "",
            "to_date": payload['to_date'] if 'to_date' in payload else ""
        }

        SubjectDelegate.export_pain_details(filters=data,user_identity=claims)
        resp = make_response('pain_details.xls')
        resp.data = open("pain_details.xls", "rb").read()
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=pain_details.xls'
        return resp


@api.route("/subject/pain/export")
class PainDetailsExport(Resource):
    """
    Class for export files
    """
    @jwt_required()
    def post(self):
        """
        Return all subjects
        """
        claims = ""

        payload = request.json
        data = {

            'subject': payload['export_fields'] if 'export_fields' in payload else [],
            "from_date": payload['from_date'] if 'from_date' in payload else "",
            "to_date": payload['to_date'] if 'to_date' in payload else ""
        }
        SubjectDelegate.export_pain_details(filters=data,user_identity=claims)
        resp = make_response('pain_details.xls')
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=subjects.xls'
        return resp


@api.route("/subject/rewards")
@api.doc(payload={'subject': 'Array of Subject IDs- 60bb10c89cf5432080d40346 ', "from_date": "%m-%d-%Y",
                  "to_date": "%m-%d-%Y", "event_type": "Array of event type names"})
class ListRewards(Resource):
    """
    Class for list rewards
    """
    @jwt_required()
    def post(self):
        """
        Return all rewards
        """
        claims = ""
        payload = request.json
        data = {
            'subject': payload['subject'] if 'subject' in payload else [],
            "event_type": payload['event_type'] if 'event_type' in payload else [],
            "from_date": payload['from_date'] if 'from_date' in payload else "",
            "to_date": payload['to_date'] if 'to_date' in payload else ""
        }

        data = RewardRedemption.list_accumulated_rewards(filters=data, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="List rewards")


@api.route("/subject/reward-redeem")
@api.doc(payload={'subject': 'Array of Subject IDs- 60bb10c89cf5432080d40346 ', "event_type": "Array of event type names"})
class ListRedemption(Resource):
    """
    Class for list Redemption
    """
    @jwt_required()
    def post(self):
        """
        Return all Redemption
        """
        claims = ""
        payload = request.json
        data = {
            'subject': payload['subject'] if 'subject' in payload else "",
            "event_type": payload['event_type'] if 'event_type' in payload else []
        }

        data = RewardRedemption.list_accumulated_reward_redemption(filters=data, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Redemption Details")


@api.route("/subject/redeem")
@api.doc(payload={'subject': 'Array of Subject IDs- 60bb10c89cf5432080d40346 ', "points": "redeem points"})
class CreateListRedemption(Resource):
    """
    Class for calculate Redemption
    """
    @jwt_required()
    def post(self):
        """
        Create all Redemption
        """
        try:
            claims = get_jwt()
            payload = request.json
            data = RewardRedemption.reward_redemption(payload, user_identity=claims)
            return Response.success(response_data=data,
                                    status_code=HttpStatusCode.OK, message="Redemption Details")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message=list(err.messages.values())[0][0])

    @jwt_required()
    def get(self):
        """
        Create all Redemption
        """
        try:
            claims = get_jwt()
            parameters = {
                'subject': ""
            }

            if 'subject' in request.args and request.args.get('subject'):
                parameters['subject'] = request.args.get('subject')

            data = RewardRedemption.list_reward_redemption(filters=parameters, user_identity=claims)
            return Response.success(response_data=data,
                                        status_code=HttpStatusCode.OK, message="Redemption Details")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message=list(err.messages.values())[0][0])


@api.route("/subject/adverse-event")
class AdverseEvent(Resource):
    """
    Class for list adverse event
    """

    @jwt_required()
    def post(self):
        """
                    API for list resource configurations
                """
        claims = get_jwt()
        parameters = {
            'limit': 10,
            'page': 1
        }
        if 'limit' in request.args and request.args.get('limit'):
            parameters['limit'] = int(request.args.get('limit'))
        if 'page_size' in request.args and request.args.get('page_size'):
            parameters['page_size'] = int(request.args.get('page_size'))
        if 'page' in request.args and request.args.get('page'):
            parameters['page'] = int(request.args.get('page'))

        payload = request.json
        data = {
            "subjects": payload["subjects"] if "subjects" in payload else [],
            "from_date": payload['from_date'] if 'from_date' in payload else "",
            "to_date": payload['to_date'] if 'to_date' in payload else ""
        }

        data = ListAdverseEvent.list_adverse_event(filters=data, parameters=parameters, user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Adverse event list")


@api.route("/subject/rating-feedback")
@api.doc(params={})
class RatingAndFeedbackDetails(Resource):
    """
    Class for listing Rating and Feedback
    """
    @jwt_required()
    def get(self):
        claims = ""
        parameters = {
            'limit': 10,
            'order': 'desc',
            'page': 1
        }
        if 'limit' in request.args and request.args.get('limit'):
            parameters['limit'] = int(request.args.get('limit'))
        if 'page' in request.args and request.args.get('page'):
            parameters['page'] = int(request.args.get('page'))

        data = RatingAndFeedbackDetailsDelegate.get_rating_feedback_details(parameters)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK,
                                message="Ratings and Feedbacks fetched succesfully")
