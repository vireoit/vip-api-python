import os
from uuid import uuid4
import pandas as pd
import json
from app import ma, response, mongo_db
from datetime import datetime, timezone
from app.subjects.schemas import SubjectImportSchema

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
            return {"messages": "Subject imported successfully", "value": True}
        except Exception as err:
            return {"messages": "Subject imported failed", "value": False, "error_data": err.messages}
    
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
            return {"messages": "Subject imported successfully", "value": True}
        except Exception as err:
            return {"messages": "Subject imported failed", "value": False, "error_data": err.messages}
