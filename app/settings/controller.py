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
from app.settings.delegates import RewardConfigurationDelegate, ResourceConfigurationDelegate, ResourceConfigurationUniqueDelegate, \
    AuditTrialFieldsListDelegate
from app.settings.schemas import RewardSchema, ResourceConfigurationSchema
from flask_restx import Api, Resource, fields

api = Namespace("Settings", description="Namespace for Settings")


@api.route("/settings/reward")
class CreateRewardConfiguration(Resource):
    """
    Class for store reward configuration
    """
    @jwt_required()
    def post(self):
        try:
            """
            Store reward
            """
            claims = ""
            payload = request.json
            RewardSchema().load({"reward_configuration": payload["RewardConfig"]})
            data = RewardConfigurationDelegate.create_reward_configuration(payload, user_identity=claims)
            return Response.success(response_data=data,
                                    status_code=HttpStatusCode.OK, message="Reward points added successfully")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message="Validation Error Occurred")

    @jwt_required()
    def get(self):
        """
        list reward
        """
        claims = ""
        data = RewardConfigurationDelegate.get_reward_configuration(user_identity=claims)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Reward configuration list")


@api.route("/settings/resources")
class ResourceConfigurationSettings(Resource):

    @jwt_required()
    def get(self):
        """
            API for list resource configurations
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

        resource_settings = ResourceConfigurationDelegate.get_resources_configuration_settings(parameters)
        return Response.success(response_data=resource_settings,
                                status_code=HttpStatusCode.OK,
                                message="Resource successfully fetched")

    @jwt_required()
    def post(self):
        """
        API to add resource configurations
        """
        try:
            payload = request.json
            ResourceConfigurationSchema().load(payload)
            data = ResourceConfigurationDelegate.add_resources_configuration_settings(payload)
            return Response.success(response_data={},
                        status_code=HttpStatusCode.OK,
                        message="Resource successfully saved")
        except ValidationError as err:
            return Response.error(next(iter(err.messages.values())), HttpStatusCode.BAD_REQUEST, message='Event saving failed')

    @jwt_required()
    def put(self):
        """
        API to update resource configurations
        """
        try:
            payload = request.json
            resource_id = payload.get('id')
            payload.pop('id')
            ResourceConfigurationSchema().load(payload)
            data = ResourceConfigurationDelegate.update_resources_configuration_settings(payload, resource_id)
            return Response.success(response_data={},
                        status_code=HttpStatusCode.OK,
                        message="Resource successfully updated")
        except ValidationError as err:
            return Response.error(next(iter(err.messages.values())), HttpStatusCode.BAD_REQUEST, message='Event updating failed')
    
    @jwt_required()
    def delete(self):
        """
        API to delete resource configurations
        """
        payload = {
            'id': request.args.get('id')
        }
        data = ResourceConfigurationDelegate.delete_resources_configuration_settings(payload)
        return Response.success(response_data={},
                    status_code=HttpStatusCode.OK,
                    message="Resource successfully deleted")
        
@api.route("/settings/resources/check")
class MasterEventUnique(Resource):
    @jwt_required()
    def get(self):
        """
            API to check whether resource configuration settings is unique
        """
        parameters = {
            'resource_title': request.args.get('resource_title') if 'resource_title' in request.args else "",
            'link': request.args.get('link') if 'link' in request.args else ""
        }
        event_data = ResourceConfigurationUniqueDelegate.check_resources_configuration_uniqueness(parameters)
        if event_data.get('is_unique') == True:
            return Response.success(response_data=event_data,
                                status_code=HttpStatusCode.OK,
                                message="{0} is available".format(event_data['key']))
        else:
            return Response.error(event_data, HttpStatusCode.BAD_REQUEST, message='{0} already exist'.format(event_data['key']))

@api.route("/settings/audit_trial/fields")
class AuditTrialFieldsList(Resource):
    @jwt_required()
    def get(self):
        parameters = {
            'field': request.args.get('field')
        }
        data = AuditTrialFieldsListDelegate.get_audit_trial_fields_list(parameters)
        return Response.success(response_data=data,
                        status_code=HttpStatusCode.OK,
                        message="Details successfully fetched")
