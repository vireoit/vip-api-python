from app import ma, response, mongo_db

import json

from flask import request
from datetime import date, datetime
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

from app.utils.mongo_encoder import format_cursor_obj
from app.utils.general import check_user_by_id
from app.exceptions import UserDoesNotExist


class AuditService:
    @staticmethod
    def create_audit_log(data, user_identity):
        user = check_user_by_id(mongo_db, user_identity)
        if not user:
            raise UserDoesNotExist

        data['actor'] = user
        data['action_type'] = request.method
        data['updated_at'] = datetime.utcnow()
        data['created_at'] = datetime.utcnow()
        data['remote_ip_address'] = request.remote_addr

        mongo_db.db.AuditLog.insert_one(data)

    @staticmethod
    def get_all_logs(data, user_identity):

        user = check_user_by_id(mongo_db, user_identity)
        if not user:
            raise UserDoesNotExist

        query_data = list(mongo_db.db.AuditLog.find({}).sort("created_at", -1))
        bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)
        return format_cursor_obj(json.loads(bs))
