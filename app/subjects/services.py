import os
from uuid import uuid4
import pandas as pd
import json
from app import ma, db, response

class SubjectImportService:
    @staticmethod
    def import_subject_csv_file(file):
        try:
            total_collection = list(db.subjects.find({}))
            data = pd.read_csv(file.stream)
            data.drop_duplicates(subset="Email", keep="first", inplace=True)
            payload = json.loads(data.to_json(orient='records'))
            for item in payload:
                if item in total_collection:
                    payload.remove(item)
            db.subjects.insert_many(payload)  
            return True
        except Exception as err:
            print(err)
    
    @staticmethod
    def import_subject_xlsx_file(file):
        try:
            total_collection = list(db.subjects.find({}))
            data = pd.read_excel(file.read())
            data.drop_duplicates(subset="Email", keep="first", inplace=True)
            payload = json.loads(data.to_json(orient='records'))
            for item in payload:
                if item in total_collection:
                    payload.remove(item)
            db.subjects.insert_many(payload)
            return True
        except Exception as err:
            print(err)
