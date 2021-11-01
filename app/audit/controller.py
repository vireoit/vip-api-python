from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Namespace, Resource
from marshmallow import ValidationError
from flask import request
from flask_restx import Api, Resource, fields


from flask_jwt_extended import get_jwt_identity
from app.response import Response
from app.flask_jwt import jwt_required
from app.status_constants import HttpStatusCode
from app.audit.schemas import CreateAuditLog
from app.audit.delegates import AuditLogDelegate
from app.utils.general import check_user_by_id

api = Namespace("Audit Log", description="Namespace for audit log")

audit_log_data = api.model('DataField', {
    'attr1': fields.String,
    'attr2': fields.String
})

audit_log_request_body = api.model('AuditLogRequest', {
    "module": fields.String(),
    "data": fields.Nested(audit_log_data),
    "action": fields.String(),
    "event": fields.String()
})


@api.route("/audit/log")
class AuditLog(Resource):
    """
    Audit log controller
    """
    @jwt_required()
    @api.expect(audit_log_request_body)
    def post(self):
        """
        Create audit log entries
        """
        try:
            payload = request.json
            CreateAuditLog().load(payload)
            current_user = get_jwt_identity()

            AuditLogDelegate.create_audit_log(payload, user_identity=current_user)
            return Response.success(response_data={},
                                    status_code=HttpStatusCode.OK, message="Audit log created successfully")
        except ValidationError as err:
            return Response.error(err.messages, HttpStatusCode.BAD_REQUEST, message="Validation Error Occurred")

    @jwt_required()
    @api.doc(params={'limit': '10 - Int', "order": "asc or desc", "page": "1 or 2 or 3 , etc - Int"})
    def get(self):
        """
        Return all logs
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

        if 'page' in request.args and request.args.get('page'):
            parameters['page'] = int(request.args.get('page'))

        data = AuditLogDelegate.get_all_logs(filters=parameters, user_identity=current_user)
        return Response.success(response_data=data,
                                status_code=HttpStatusCode.OK, message="Audit log list")
