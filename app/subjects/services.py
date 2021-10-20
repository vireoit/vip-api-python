import os
import pandas as pd
import json
import pytz

from uuid import uuid4
from datetime import datetime, timezone, date
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

from app import ma, response, mongo_db
from app.subjects.schemas import SubjectImportSchema
from app.subjects.export import export_table_data, export_pain_data
from app.utils.mongo_encoder import format_cursor_obj
from app.utils.data_format_service_util import list_string_to_string
from app.utils.http_service_util import perform_http_request
from app.base_urls import VIP_ADMIN_URL, VIP_BACKEND_URL

class SubjectImportService:
    @staticmethod
    def send_activation_email(inactive_subjects_query, parameters):
        for sub in inactive_subjects_query:
            bs = dumps(sub, json_options=RELAXED_JSON_OPTIONS)
            val  = format_cursor_obj(json.loads(bs))
            email_id = val['Email']
            user_id = val['_id']
            response_data = perform_http_request(f'{VIP_BACKEND_URL}/api/Mail/Activation?email={email_id}&userId={user_id}', parameters['authorization'], 
                body={}, request_method="POST")
        return    
            
    @staticmethod
    def format_file(data):
        data.columns = data.columns.str.replace(' ', '')
        data.drop_duplicates(subset=['Email', 'Phone'], keep="first", inplace=True)
        data['AddedOn'] = datetime.now().replace(microsecond=0).isoformat()
        data['LastUpdatedOn'] = datetime.now().replace(microsecond=0).isoformat()
        data['Password'] = ''
        data['IsActive'] = False
        data['UserType'] = "Patient"
        data['IsDeleted'] = False
        data['FitBitAccessToken'] = None
        data['UserStatus'] = ''
        data['ActivatedOn'] = datetime.now().replace(microsecond=0).isoformat()
        data["Phone"] = data["Phone"].astype(str)
        data["PostalCode"] = data["PostalCode"].astype(str)
        data['ProfilePic'] = None
        data['Notes'] = None
        data['ResetMailSentDate'] = None
        data['IsMailExpired'] = False


    @staticmethod
    def import_subject_csv_file(file, parameters):
        try:
            data = pd.read_csv(file.stream)
            SubjectImportService.format_file(data)
            payload = json.loads(data.to_json(orient='records'))
            repeat_list = payload[:]
            for item in repeat_list:
                email_id = item['Email']
                phone_no = item['Phone']
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            SubjectImportSchema().load({"subjects": payload})
            for rt in payload:
                rt['RefreshTokens'] = [{
                    "_id": "",
                    "Token": "",
                    "Expires": datetime.now().replace(microsecond=0).isoformat(),
                    "Created": datetime.now().replace(microsecond=0).isoformat(),
                    "CreatedByIp": "",
                    "Revoked": None,
                    "RevokedByIp": None,
                    "ReplacedByToken": ""
                }]
            if payload:
                mongo_db.db.Subjects.insert_many(payload)
            else:
                pass
            inactive_subjects_query = mongo_db.db.Subjects.find({"IsActive": False})	
            SubjectImportService.send_activation_email(inactive_subjects_query, parameters)
            return {"message": "Subject imported successfully", "value": True}
        except Exception as err:
            error = err.messages
            return {"message": "Subject imported failed", "value": False, "error_data": next(iter(error.values()))}
    
    @staticmethod
    def import_subject_excel_file(file, parameters):
        try:
            data = pd.read_excel(file.read())
            SubjectImportService.format_file(data)
            payload = json.loads(data.to_json(orient='records'))
            repeat_list = payload[:]
            for item in repeat_list:
                email_id = item['Email']
                phone_no = item['Phone']
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            SubjectImportSchema().load({"subjects": payload})
            for rt in payload:
                rt['RefreshTokens'] = [{
                    "_id": "",
                    "Token": "",
                    "Expires": datetime.now().replace(microsecond=0).isoformat(),
                    "Created": datetime.now().replace(microsecond=0).isoformat(),
                    "CreatedByIp": "",
                    "Revoked": None,
                    "RevokedByIp": None,
                    "ReplacedByToken": ""
                }]
            if payload:
                mongo_db.db.Subjects.insert_many(payload)
            else:
                pass
            inactive_subjects_query = mongo_db.db.Subjects.find({"IsActive": False})
            SubjectImportService.send_activation_email(inactive_subjects_query, parameters)
            return {"message": "Subject imported successfully", "value": True}
        except Exception as err:
            error = err.messages
            return {"message": "Subject imported failed", "value": False, "error_data": next(iter(error.values()))}


class SubjectService:
    @staticmethod
    def export_subjects(data, user_identity):
        pain_details = SubjectService.pain_details_fetch(data, user_identity)
        data = data.get('export_fields')
        data = tuple(data)
        query_data = list(mongo_db.db.Subjects.find({"IsDeleted": False, "UserType": "Patient",
                                                     "IsActive": True}, data))
        all_data = []
        for data in query_data:
            all_data.append(data)
        data_file = export_table_data(all_data, pain_details)
        return data_file

    @staticmethod
    def pain_details(data, user_identity):
        in_date = data['date']
        start_date = datetime.strptime(str(in_date)+" 00", "%m-%d-%Y %H")
        end_date = datetime.strptime(str(in_date)+" 23", "%m-%d-%Y %H")
        query_data = mongo_db.db.Logs.find_one({"DateOfLog": {"$lte": end_date, '$gt': start_date},
                                            "Subject._id": ObjectId(data['subject']), "IsActive": True})

        bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)

        return format_cursor_obj(json.loads(bs))

    @staticmethod
    def pain_details_fetch(data, user_identity):
        if data['from_date']:
            start_date = datetime.strptime(str(data['from_date']) + " 00", "%m-%d-%Y %H")
        else:
            start_date = ""
        if data['to_date']:
            end_date = datetime.strptime(str(data['to_date']) + " 23", "%m-%d-%Y %H")
        else:
            end_date = ""
        query_data = mongo_db.db.Logs.find({"IsActive": True, "DateOfLog": {"$lte": end_date, '$gte': start_date}})
        all_data = []
        for data in query_data:
            data['Subject Name'] = data['Subject']['Name']
            t = data['DateOfLog']
            data['Date'] = t.strftime('%m/%d/%Y')
            data['Triggers'] = list_string_to_string(data['Triggers'])
            data['PainType'] = list_string_to_string(data['PainType'])
            data['Sleep'] = list_string_to_string(data['Sleep'])
            data['Treatments'] = list_string_to_string(data['Treatments'])
            data['PainLocation'] = list_string_to_string(data['PainLocation'])
            all_medications = []
            if data['Medications']:
                for value in data['Medications']:
                    medications = value['Medication']['Name']+", " + value['Dosage']
                    all_medications.append(medications)
                data['Medications'] = list_string_to_string(all_medications)
            else:
                data['Medications'] = None
            json_file = open("app/configuration/pain_level.json")
            json_data = json.load(json_file)
            list_items = [data_dict for data_dict in json_data if str(data_dict["id"]) in data['LevelOfPain']]
            if len(list_items) > 0:
                list_items = list_items[0]
            data['Pain Level'] = list_items['title']+", "+list_items['description']
            keys = ['Subject', 'IsActive', 'LastUpdatedOn', 'AddedOn', 'Notes', 'BodySide', 'DateOfLog', 'LevelOfPain']
            list(map(data.pop, keys))
            all_data.append(data)
        return all_data

    @staticmethod
    def export_pain_details(data, user_identity):

        if data['from_date']:
            start_date = datetime.strptime(str(data['from_date']) + " 00", "%m-%d-%Y %H")
        else:
            start_date = ""
        if data['to_date']:
            end_date = datetime.strptime(str(data['to_date']) + " 23", "%m-%d-%Y %H")
        else:
            end_date = ""
        all_subjects = []
        for subject in data['subject']:
            subject = ObjectId(subject)
            all_subjects.append(subject)

        query_data = mongo_db.db.Logs.find({"Subject._id": {"$in": tuple(all_subjects)}, "IsActive": True,
                                            "DateOfLog": {"$lte": end_date, '$gte': start_date}})
        print(query_data)
        all_data = []
        for data in query_data:
            data['Subject Name'] = data['Subject']['Name']
            t = data['DateOfLog']
            data['Date'] = t.strftime('%m/%d/%Y')
            data['Triggers'] = list_string_to_string(data['Triggers'])
            data['PainType'] = list_string_to_string(data['PainType'])
            data['Sleep'] = list_string_to_string(data['Sleep'])
            data['Treatments'] = list_string_to_string(data['Treatments'])
            data['PainLocation'] = list_string_to_string(data['PainLocation'])
            all_medications = []
            if data['Medications']:
                for value in data['Medications']:
                    medications = value['Medication']['Name']+", " + value['Dosage']
                    all_medications.append(medications)
                data['Medications'] = list_string_to_string(all_medications)
            else:
                data['Medications'] = None
            json_file = open("app/configuration/pain_level.json")
            json_data = json.load(json_file)
            list_items = [data_dict for data_dict in json_data if str(data_dict["id"]) in data['LevelOfPain']]
            if len(list_items) > 0:
                list_items = list_items[0]
            data['Pain Level'] = list_items['title']+", "+list_items['description']
            keys = ['Subject', 'IsActive', 'LastUpdatedOn', 'AddedOn', 'Notes', 'BodySide', 'DateOfLog', 'LevelOfPain']
            list(map(data.pop, keys))
            all_data.append(data)
        data_file = export_pain_data(all_data)
        return data_file

