from pymongo.message import delete
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
from app.masters.delegates import AdminListDelegate, MasterEventDelegate
from app.masters.schemas import MasterEventSchema
from flask_restx import Api, Resource, fields


api = Namespace("Master", description="Namespace for Master")


@api.route("/master/admin")
class MasterAdmin(Resource):
    # @jwt_required
    def get(self):
        """
            API for list all admin for master
        """
        parameters = {
            'limit': 10,
            'order': 'desc'
        }
        if 'limit' in request.args and request.args.get('limit'):
            parameters['limit'] = int(request.args.get('limit'))
        if 'page_size' in request.args and request.args.get('page_size'):
            parameters['page_size'] = int(request.args.get('page_size'))
        if 'order' in request.args and request.args.get('order'):
            parameters['order'] = str(request.args.get('order'))
        if 'search' in request.args and request.args.get('search'):
            parameters['search'] = str(request.args.get('search'))
        
        admin_data = AdminListDelegate.get_admin_list(parameters)
        return Response.success(response_data=admin_data,
                                status_code=HttpStatusCode.OK,
                                message="Admin list fetched succesfully")


@api.route("/master/event")
class MasterEvent(Resource):
    # @jwt_required
    # def get(self):
    #     """
    #         API for list all event for master
    #     """
    #     parameters = {
    #         'limit': 10,
    #         'order': 'desc'
    #     }
    #     if 'limit' in request.args and request.args.get('limit'):
    #         parameters['limit'] = int(request.args.get('limit'))
    #     if 'page_size' in request.args and request.args.get('page_size'):
    #         parameters['page_size'] = int(request.args.get('page_size'))
    #     if 'order' in request.args and request.args.get('order'):
    #         parameters['order'] = str(request.args.get('order'))
    #     if 'search' in request.args and request.args.get('search'):
    #         parameters['search'] = str(request.args.get('search'))
        
    #     admin_data = MasterEventListAddDelegate.get_event_list(parameters)
    #     return Response.success(response_data=admin_data,
    #                             status_code=HttpStatusCode.OK,
    #                             message="Event list fetched succesfully")

    # @jwt_required
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

#     @jwt_required
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
    
    # @jwt_required
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
        
