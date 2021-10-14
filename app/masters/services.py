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
from bson.objectid import ObjectId


class AdminListService:
    @staticmethod
    def get_admin_list(parameters):
        sorted_by = parameters.get('order')
        limit_by = parameters.get('limit')
        search_by = parameters.get('search')
        if sorted_by == "desc":
            order_by = -1
        else:
            order_by = 1
        if search_by is not None:
            mongo_db.db.Subjects.create_index([('Name', 'text')])
            query_data = mongo_db.db.Subjects.find({"$text": {"$search": search_by}})
        else:
            query_data = mongo_db.db.Subjects.find({"$and":[{"UserType": "Admin"}, {"IsDeleted": False}]}) \
                .sort("AddedOn", order_by).limit(limit_by)
        admin_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val  = format_cursor_obj(json.loads(bs))
            admin_list.append(val)
        return admin_list

class MasterEventService:
    @staticmethod
    def get_event_list(parameters):
        sorted_by = parameters.get('order')
        limit_by = parameters.get('limit')
        search_by = parameters.get('search')
        if sorted_by == "desc":
            order_by = -1
        else:
            order_by = 1
        if search_by is not None:
            mongo_db.db.Events.create_index([('event_type', 'text')])
            query_data = mongo_db.db.Events.find({"$text": {"$search": search_by}})
        else:
            query_data = mongo_db.db.Events.find().sort("created_on", order_by).limit(limit_by)
        event_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val  = format_cursor_obj(json.loads(bs))
            event_list.append(val)
        return event_list

    @staticmethod
    def add_master_event(payload):
        try:
            payload['created_on'] = datetime.now().replace(microsecond=0).isoformat()
            payload['updated_on'] = datetime.now().replace(microsecond=0).isoformat()
            payload['is_active'] = True
            mongo_db.db.Events.insert_one(payload)
            return True
        except Exception as err:
            print(err)

    @staticmethod
    def update_master_event(payload, event_id):
        try:
            payload['updated_on'] = datetime.now().replace(microsecond=0).isoformat()
            mongo_db.db.Events.find_one_and_update({'_id': ObjectId(event_id)},  {'$set': payload}) 
            return True
        except Exception as err:
            print(err)

    @staticmethod
    def delete_master_event(payload):
        try:
            event_id = payload['id']
            mongo_db.db.Events.remove({"_id": ObjectId(event_id)})
            return True
        except Exception as err:
            print(err)
