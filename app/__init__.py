from flask import Flask, jsonify
from flask_restx import Api
from flask_marshmallow import Marshmallow
from .status_constants import HttpStatusCode, BusinessErrorCode
from .response import Response
from flask_pymongo import PyMongo


db = PyMongo()
ma = Marshmallow()


def create_app(env=None):
    from app.config import config_by_name
    from app.routes import register_routes

    app = Flask(__name__)
    app.config.from_object(config_by_name[env or 'test'])
    db.init_app(app)
    ma.init_app(app)


    from flask import Blueprint

    api_v1 = Blueprint('api_v1', __name__)

    api = Api(api_v1,
              title="In Scholaris API",
              version="0.1.0", )

    register_routes(api, app)

    app.register_blueprint(api_v1, url_prefix="/vip")

    @app.route("/health")
    def health():
        return Response.success({"status": "Running"}, HttpStatusCode.CREATED, "Successfully working")

    @app.route("/raise_form_error")
    def form_error():
        return Response.error(
            {"name": "Required"},
            HttpStatusCode.BAD_REQUEST,
            "Field Required",
            BusinessErrorCode.INVALID_USER)

    @api.errorhandler(TypeError)
    def handle_type_error_exception(error):
        return Response.error(
            {"exception": str(error)},
            HttpStatusCode.BAD_REQUEST,
            str(error),
        )


    return app

