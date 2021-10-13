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
from app.subjects.delegates import SubjectImportDelegate
from app.subjects.delegates import SubjectDelegate
from flask_restx import Api, Resource, fields


api = Namespace("Subject", description="Namespace for Subject")

export_fields = api.model('ExportFields', {
    'export_fields': fields.List(fields.String)
})


@api.route("/subject/import")
class SubjectImport(Resource):
    #@jwt_required
    def post(self):
        payload = request.files
        try:
            if 'import_file' in payload:
                file = payload['import_file']
                extension = file.filename.rsplit('.', 1)[1].lower()
                if file.filename == '':
                    raise FileNotSelected(param_name='import_file')
                if file and file_service_util.allowed_document_types(file.filename):
                    if extension == "csv":
                        response = SubjectImportDelegate.import_subject_csv_file(file)
                    if extension == "xlsx" or extension == "xls":
                        response = SubjectImportDelegate.import_subject_xlsx_file(file)
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
# @api.doc(params={'export_fields': "array of fields"})
class SubjectExport(Resource):
    """
    Class for export files
    """
    # @jwt_required()
    @api.expect(export_fields)
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
                                status_code=HttpStatusCode.OK, message="Pain Details")


@api.route("/subject/pain/export")
class PainDetailsExport(Resource):
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

            'subject': payload['export_fields'] if 'export_fields' in payload else [],
            "from_date": payload['from_date'] if 'from_date' in payload else "",
            "to_date": payload['to_date'] if 'to_date' in payload else ""
        }
        SubjectDelegate.export_pain_details(filters=data,user_identity=claims)
        resp = make_response('pain_details.xls')
        resp.headers['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
        resp.headers['Content-Disposition'] = 'attachment;filename=subjects.xls'
        return resp