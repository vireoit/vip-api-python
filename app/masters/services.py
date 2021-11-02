import os
import pandas as pd
import json
from pymongo.message import query
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
        page = parameters.get('page')
        order_by = -1 if sorted_by == "desc" else 1
        total_count = mongo_db.db.Subjects.find({"$and":[{"UserType": "Admin"}, {"IsDeleted": False}]}).count()
        if search_by is not None:
            query_data = mongo_db.db.Subjects.find({"Name": {"$regex": "{0}".format(search_by), '$options' : 'i'}}).skip((page-1) * limit_by).limit(limit_by)
        else:
            query_data = mongo_db.db.Subjects.find({"$and":[{"UserType": "Admin"}, {"IsDeleted": False}]})\
                .skip((page-1) * limit_by).limit(limit_by).sort("AddedOn", order_by).limit(limit_by)
        admin_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val  = format_cursor_obj(json.loads(bs))
            admin_list.append(val)
        response_data = {
            'admin_list': admin_list,
            'total_count': total_count
        }
        return response_data

class MasterEventService:
    @staticmethod
    def get_event_list(parameters):
        sorted_by = parameters.get('order')
        limit_by = parameters.get('limit')
        search_by = parameters.get('search')
        order_by = -1 if sorted_by == "desc" else 1
        page = parameters.get("page")
        total_count = mongo_db.db.Events.find({}).count()
        if search_by is not None:
            query_data = mongo_db.db.Events.find({"event_type": {"$regex": "{0}".format(search_by), '$options' : 'i'}}).skip((page-1) * limit_by).limit(limit_by)
        else:
            query_data = mongo_db.db.Events.find().skip((page-1) * limit_by).limit(limit_by).sort("created_on", order_by).limit(limit_by)

        allpost = mongo_db.db.Events.find().skip((page-1) * limit_by).limit(limit_by)
        bs = dumps(allpost, json_options=RELAXED_JSON_OPTIONS)
        event_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            event_list.append(val)
        response_data = {
            'event_list': event_list,
            'total_count': total_count
        }
        return response_data

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


    @staticmethod
    def list_event_list():

        query_data = list(mongo_db.db.Events.find())
        # bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)
        event_list = []
        for data in query_data:
            dict = {}
            dict['_id'] = data['_id']
            dict['event_type'] = data['event_type']
            bs = dumps(dict, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            event_list.append(val)

        return event_list


class MasterEventUniqueService:
    @staticmethod
    def check_event_type_uniqueness(parameters):
        query_data = mongo_db.db.Events.find_one({"event_type": parameters.get('event_type')})
        if query_data:
            return {'is_unique': False}
        return {'is_unique': True}


class MedicationImportService:

    @staticmethod
    def import_medication_xlsx_file(file):
        try:
            data = pd.read_excel(file.read())
            data.columns = data.columns.str.replace(' ', '')
            data.drop_duplicates(subset=['MedicationName'], keep="first", inplace=True)
            payload = json.loads(data.to_json(orient='records'))
            MedicationImportSchema().load({"medication": payload})
            repeat_list = payload[:]
            for item in repeat_list:
                if item['ProductType'] == "Vireo health product":
                    item['IsVireoProduct'] = True
                else:
                    item['IsVireoProduct'] = False
                name = item['MedicationName']
                item_exist = mongo_db.db.Products.find_one({"Name": name})
                if item_exist and (item_exist['Name'] == name):
                    payload.remove(item)
            if payload:
                all_data = []
                for item in payload:
                    item.pop('ProductType')
                    item['Name'] = item.pop('MedicationName')
                    item['CreatedOn'] = datetime.utcnow()
                    item['LastUpdatedOn'] = datetime.utcnow()
                    item['IsActive'] = True
                    item['Amount'] = item['Amount'] if item['Amount'] else 0
                    all_data.append(item)
                print(all_data)
                mongo_db.db.Products.insert_many(all_data)
            else:
                pass
            return {"message": "Medication imported successfully", "value": True}
        except Exception as err:
            error = err.messages
            return {"message": "Medication imported failed", "value": False, "error_data": next(iter(error.values()))}