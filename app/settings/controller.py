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
from app.settings.delegates import RewardConfigurationDelegate
from app.settings.schemas import RewardSchema
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
                                    status_code=HttpStatusCode.OK, message="Reward configuration created")
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
