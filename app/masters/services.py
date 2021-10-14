import os
import pandas as pd
import json
import pytz

from uuid import uuid4
from datetime import datetime, timezone, date
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

from app import ma, response, mongo_db
from app.utils.mongo_encoder import format_cursor_obj
from app.utils.data_format_service_util import list_string_to_string


class AdminListService:
    @staticmethod
    def get_admin_list(parameters):
        sorted_by = parameters.get('order')
        limit_by = parameters.get('limit')
        if sorted_by == "desc":
            order_by = -1
        else:
            order_by = 1
        query_data = mongo_db.db.Subjects.find({"$and":[{"UserType": "Admin"}, {"IsDeleted": False}]}) \
            .sort("AddedOn", order_by).limit(limit_by)
        admin_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val  = format_cursor_obj(json.loads(bs))
            admin_list.append(val)
        return admin_list
      