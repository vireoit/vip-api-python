from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from app.response import Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_constants import HttpStatusCode
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
# from app import constants
from app.subjects.delegates import SubjectImportDelegate

api = Namespace("Subject", description="Namespace for Subject")


"""
API for subject import
"""

@api.route("v1/subject/import")
class Employer(Resource):
    @jwt_required
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
                return Response.success(response_data={}, status_code=HttpStatusCode.OK, message=response['messages'])
            else:
                if not response['messages']:
                    response['messages'] = "Subject import failed"
                return Response.error(error_data=response['error_data'], status_code=HttpStatusCode.BAD_REQUEST, 
                    message=response['messages'])
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message=list(err.messages.values())[0][0])
