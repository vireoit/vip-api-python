import os
import pandas as pd
import json
import pytz

from uuid import uuid4
from datetime import datetime, timezone, date
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import jsonify
from six import ensure_str

from app import ma, response, mongo_db
from app.subjects.schemas import SubjectImportSchema
from app.subjects.export import export_table_data


class SubjectImportService:
    @staticmethod
    def import_subject_csv_file(file):
        try:
            data = pd.read_csv(file.stream)
            data['AddedOn'] = datetime.now().replace(microsecond=0).isoformat()
            data.columns = data.columns.str.replace(' ', '')
            data.drop_duplicates(subset=['Email', 'Phone'], keep="first", inplace=True)
            payload = json.loads(data.to_json(orient='records'))
            repeat_list = payload[:]
            for item in repeat_list:
                email_id = item['Email']
                phone_no = item['Phone']
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            SubjectImportSchema().load({"subjects": payload})
            if payload:
                mongo_db.db.Subjects.insert_many(payload)
            else:
                pass
            return {"message": "Subject imported successfully", "value": True}
        except Exception as err:
            return {"message": "Subject imported failed", "value": False, "error_data": err.messages}
    
    @staticmethod
    def import_subject_xlsx_file(file):
        try:
            data = pd.read_excel(file.read())
            data['AddedOn'] = datetime.now().replace(microsecond=0).isoformat()
            data.columns = data.columns.str.replace(' ', '')
            data.drop_duplicates(subset=['Email', 'Phone'], keep="first", inplace=True)
            payload = json.loads(data.to_json(orient='records'))
            repeat_list = payload[:]
            for item in repeat_list:
                email_id = item['Email']
                phone_no = item['Phone']
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            SubjectImportSchema().load({"subjects": payload})
            if payload:
                mongo_db.db.Subjects.insert_many(payload)
            else:
                pass
            return {"message": "Subject imported successfully", "value": True}
        except Exception as err:
            return {"message": "Subject imported failed", "value": False, "error_data": err.messages}


class SubjectService:
    @staticmethod
    def export_subjects(data, user_identity):
        data = data.get('export_fields')
        data = tuple(data)
        query_data = list(mongo_db.db.Subjects.find({}, data))
        all_data = []
        for data in query_data:
            all_data.append(data)
        data_file = export_table_data(all_data)
        return data_file

    @staticmethod
    def pain_details(data, user_identity):
        print(data['date'])
        in_date = data['date']
        start_date = datetime.strptime(str(in_date)+" 00", "%m-%d-%Y %H")
        end_date = datetime.strptime(str(in_date)+" 23", "%m-%d-%Y %H")
        query_data = mongo_db.db.Logs.find_one({"DateOfLog": {"$lte": end_date, '$gt': start_date},
                                            "Subject._id": ObjectId(data['subject']), "IsActive": True})

        query_data['_id'] = str(query_data['_id'])
        query_data['Subject']['_id'] = str(query_data['Subject']['_id'])
        print(query_data)
        # list_cur = list(query_data)
        json_data = dumps(query_data)

        print(json.dumps(json_data))
        return json.dumps(json_data)




    @staticmethod
    def export_pain_details(data, user_identity):
        pass