from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from app.response import Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.status_constants import HttpStatusCode
# from app.utils import file_service_util
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
    # @jwt_required
    def post(self):
        # current_user = get_jwt_identity()
        payload = request.files
        try:
            if 'import_file' in payload:
                file = payload['import_file']
                extension = file.filename.rsplit('.', 1)[1].lower()
                if file.filename == '':
                    raise FileNotSelected(param_name='import_file')
                if file and file_service_util.allowed_document_types(file.filename):
                    if extension == "csv":
                        imported_document = SubjectImportDelegate.import_subject_csv_file(file)
                    if extension == "xlsx":
                        imported_document = SubjectImportDelegate.import_subject_xlsx_file(file)
                else:
                    raise FileFormatException(param_name='types are csv/xlsx')
            if imported_document == True:
                message = {"message": "Subject imported successfully"}
                return Response.success(response_data={}, status_code=HttpStatusCode.OK, **message)
            else:
                message = {"message": "Subject import failed"}
                return Response.error(error_data={}, status_code=HttpStatusCode.BAD_REQUEST, **message)
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST)
