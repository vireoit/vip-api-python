from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from app.response import Response
from flask_jwt_extended import get_jwt_identity
from app.status_constants import HttpStatusCode

from app.masters.delegates import AdminListDelegate, MasterEventDelegate, MedicationImportDelegate, MasterEventUniqueDelegate
from app.exceptions import FileNotSelected, FileUploadException, FileFormatException
from app.utils import file_service_util
from app.masters.schemas import MasterEventSchema
from flask_restx import Api, Resource, fields
from app.flask_jwt import jwt_required


api = Namespace("Master", description="Namespace for Master")


@api.route("/master/admin")
class MasterAdmin(Resource):

    @jwt_required()
    @api.doc(params={'limit': "Limit per page - Int", "order": "desc or asc", "search": "Search with event name",
                     "page": "Page number - Int"})
    def get(self):
        """
            API for list all admin for master
        """
        parameters = {
            'limit': 10,
            'order': 'desc',
            'page': 1
        }
        if 'limit' in request.args and request.args.get('limit'):
            parameters['limit'] = int(request.args.get('limit'))
        if 'page_size' in request.args and request.args.get('page_size'):
            parameters['page_size'] = int(request.args.get('page_size'))
        if 'order' in request.args and request.args.get('order'):
            parameters['order'] = str(request.args.get('order'))
        if 'search' in request.args and request.args.get('search'):
            parameters['search'] = str(request.args.get('search'))
        if 'page' in request.args and request.args.get('page'):
            parameters['page'] = int(request.args.get('page'))
        
        admin_data = AdminListDelegate.get_admin_list(parameters)
        return Response.success(response_data=admin_data,
                                status_code=HttpStatusCode.OK,
                                message="Admin list fetched succesfully")


@api.route("/master/event")
class MasterEvent(Resource):

    @jwt_required()
    @api.doc(params={'limit': "Limit per page - Int", "order": "desc or asc", "search": "Search with event name",
                     "page": "Page number - Int"})
    def get(self):
        """
            API for list all event for master
        """
        current_user = get_jwt_identity()
        parameters = {
            'limit': 10,
            'order': 'desc',
            'page': 1
        }
        if 'limit' in request.args and request.args.get('limit'):
            parameters['limit'] = int(request.args.get('limit'))
        if 'page_size' in request.args and request.args.get('page_size'):
            parameters['page_size'] = int(request.args.get('page_size'))
        if 'order' in request.args and request.args.get('order'):
            parameters['order'] = str(request.args.get('order'))
        if 'search' in request.args and request.args.get('search'):
            parameters['search'] = str(request.args.get('search'))
        if 'page' in request.args and request.args.get('page'):
            parameters['page'] = int(request.args.get('page'))

        event_data = MasterEventDelegate.get_event_list(parameters)
        return Response.success(response_data=event_data,
                                status_code=HttpStatusCode.OK,
                                message="Event list fetched succesfully")

    @jwt_required()
    def post(self):
        """
        API to add events on master
        """
        try:
            payload = request.json
            MasterEventSchema().load(payload)
            data = MasterEventDelegate.add_master_event(payload)
            return Response.success(response_data={},
                        status_code=HttpStatusCode.OK,
                        message="Event successfully saved")
        except ValidationError as err:
            return Response.error(next(iter(err.messages.values())), HttpStatusCode.BAD_REQUEST, message='Event saving failed')

    @jwt_required()
    def put(self):
        """
        API to update events on master
        """
        try:
            payload = request.json
            event_id = payload.get('id')
            payload.pop('id')
            MasterEventSchema().load(payload)
            data = MasterEventDelegate.update_master_event(payload, event_id)
            return Response.success(response_data={},
                        status_code=HttpStatusCode.OK,
                        message="Event successfully updated")
        except ValidationError as err:
            return Response.error(next(iter(err.messages.values())), HttpStatusCode.BAD_REQUEST, message='Event updating failed')
    
    @jwt_required()
    def delete(self):
        """
        API to delete events on master
        """
        payload = {
            'id': request.args.get('id')
        }
        data = MasterEventDelegate.delete_master_event(payload)
        return Response.success(response_data={},
                    status_code=HttpStatusCode.OK,
                    message="Event successfully deleted")
        
@api.route("/master/event/check")
class MasterEventUnique(Resource):
    @jwt_required()
    def get(self):
        """
            API to check whether an event type is unique
        """
        parameters = {
            'event_type': request.args.get('event_type') if 'event_type' in request.args else ""
        }
        event_data = MasterEventUniqueDelegate.check_event_type_uniqueness(parameters)
        if event_data.get('is_unique') == True:
            return Response.success(response_data=event_data,
                                status_code=HttpStatusCode.OK,
                                message="Event type is available")
        else:
            return Response.error(event_data, HttpStatusCode.BAD_REQUEST, message='Event type already exist')


@api.route("/master/medication/import")
class MedicationImport(Resource):
    @jwt_required()
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
                        response = MedicationImportDelegate.import_medication_xlsx_file(file)
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


@api.route("/master/events")
class ListMasterEvent(Resource):

    @jwt_required()
    def get(self):
        """
            API for list all event for master
        """
        event_data = MasterEventDelegate.list_event_list()
        return Response.success(response_data=event_data,
                                status_code=HttpStatusCode.OK,
                                message="Event list fetched succesfully")
