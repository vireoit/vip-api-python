import requests
from flask import request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import Response as flask_response
from app.response import Response
from app.status_constants import HttpStatusCode

import json

api = Namespace("VIP", description="Namespace for VIP API Services")


@api.route("/metadata")
class MetaData(Resource):
    """
    Class for handle CoOpJobs end points
    """
    def get(self):
        """
        Return all jobs
        """
        return Response.error("", HttpStatusCode.BAD_REQUEST)
