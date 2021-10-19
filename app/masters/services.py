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
from app.masters.schemas import MedicationImportSchema
from bson.objectid import ObjectId


class AdminListService:
    @staticmethod
    def get_admin_list(parameters):
        sorted_by = parameters.get('order')
        limit_by = parameters.get('limit')
        search_by = parameters.get('search')
        order_by = -1 if sorted_by == "desc" else 1
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
        order_by = -1 if sorted_by == "desc" else 1
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


class MedicationImportService:

    @staticmethod
    def import_medication_xlsx_file(file):
        try:
            data = pd.read_excel(file.read())
            data['CreatedOn'] = datetime.utcnow()
            data['LastUpdatedOn'] = datetime.utcnow()
            data['IsActive'] = True
            data.columns = data.columns.str.replace(' ', '')
            data.drop_duplicates(subset=['Name'], keep="first", inplace=True)
            payload = json.loads(data.to_json(orient='records'))
            MedicationImportSchema().load({"medication": payload})
            repeat_list = payload[:]
            for item in repeat_list:
                if item['IsVireoProduct'] == "yes" or item['IsVireoProduct'] == "Yes":
                    item['IsVireoProduct'] = True
                else:
                    item['IsVireoProduct'] = False

                name = item['Name']
                item_exist = mongo_db.db.Products.find_one({"Name": name})
                if item_exist and (item_exist['Name'] == name):
                    payload.remove(item)

            print(payload)
            if payload:
                mongo_db.db.Products.insert_many(payload)
            else:
                pass
            return {"message": "Medication imported successfully", "value": True}
        except Exception as err:
            error = err.messages
            return {"message": "Medication imported failed", "value": False, "error_data": next(iter(error.values()))}