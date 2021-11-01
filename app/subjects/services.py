import os
import pandas as pd
import json
import pytz

from uuid import uuid4
from datetime import datetime, timezone, date, timedelta
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from bson.codec_options import CodecOptions
from dateutil.tz import tzutc, tzlocal

from app import ma, response, mongo_db
from app.subjects.schemas import SubjectImportSchema
from app.subjects.export import export_table_data, export_pain_data
from app.utils.mongo_encoder import format_cursor_obj
from app.utils.data_format_service_util import list_string_to_string
from app.utils.http_service_util import perform_http_request
from app.base_urls import VIP_ADMIN_URL, VIP_BACKEND_URL
from statistics import mode

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
        data['Password'] = ''
        data['IsActive'] = False
        data['UserType'] = "Patient"
        data['IsDeleted'] = False
        data['FitBitAccessToken'] = None
        data['UserStatus'] = ''
        data["Phone"] = data["Phone"].astype(str)
        data["PostalCode"] = data["PostalCode"].astype(str)
        data['ProfilePic'] = None
        data['Notes'] = None
        data['ResetMailSentDate'] = None
        data['IsMailExpired'] = False
        data['LastPasswordUpdatedDate'] = None


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
                if phone_no[0] != "+":
                    item['Phone'] = "+1" +"-("+phone_no[0:3]+")"+" "+phone_no[3:6]+"-"+phone_no[6:]
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            SubjectImportSchema().load({"subjects": payload})
            for rt in payload:
                rt['ActivatedOn'] = datetime.utcnow()
                rt['AddedOn'] = datetime.utcnow()
                rt['LastUpdatedOn'] = datetime.utcnow()
                rt['RefreshTokens'] = [{
                    "_id": "",
                    "Token": "",
                    "Expires": datetime.utcnow(),
                    "Created": datetime.utcnow(),
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
                if phone_no[0] != "+":
                    item['Phone'] = "+1" +"-("+phone_no[0:3]+")"+" "+phone_no[3:6]+"-"+phone_no[6:]
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            SubjectImportSchema().load({"subjects": payload})
            for rt in payload:
                rt['ActivatedOn'] = datetime.utcnow()
                rt['AddedOn'] = datetime.utcnow()
                rt['LastUpdatedOn'] = datetime.utcnow()
                rt['RefreshTokens'] = [{
                    "_id": "",
                    "Token": "",
                    "Expires": datetime.utcnow(),
                    "Created": datetime.utcnow(),
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
        insights = data.get('personal_insights')
        data = data.get('export_fields')
        if insights == True:
            insights_data = SubjectService.get_personal_insights()
        else:
            insights_data = []
        data = tuple(data)
        query_data = list(mongo_db.db.Subjects.find({"IsDeleted": False, "UserType": "Patient"}, data))
        all_data = []
        for data in query_data:
            all_data.append(data)
        data_file = export_table_data(all_data, pain_details, insights_data)
        return data_file

    @staticmethod
    def add_multiple_pains(lop_list):
        lop_list = sum([int(i) for i in lop_list])
        return lop_list

    @staticmethod
    def extract_pain_data(query_data, json_data):
        query_list = list(query_data)
        if query_list:
            sum = 0
            sleep_list = []
            for data in query_list:
                sleep_list.append(data['Sleep'][0])
                sum = sum + int(SubjectService.add_multiple_pains(data['LevelOfPain']))
            sleep = mode(sleep_list)   
            lop = sum//len(query_list)
            lop_list = list(str(lop))
            for data_dict in json_data:
                if str(data_dict["id"]) in lop_list:
                    pain_level = data_dict['title']
            return pain_level, sleep
        else:
            return "", ""

    @staticmethod
    def format_dates(frequency):
        if frequency == "Today":
            date_today = date.today()
            start_date = datetime.strptime(str(date_today) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
        elif frequency == "Weekly":
            date_today = date.today()
            week_ago = date_today - timedelta(days=7)
            start_date = datetime.strptime(str(week_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
        elif frequency == "Monthly":
            date_today = date.today()
            month_ago = date_today - timedelta(days=30)
            start_date = datetime.strptime(str(month_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
        return start_date, end_date

    @staticmethod
    def format_insight_datas(start_date, end_date, subs_id):
        insight = mongo_db.db.Logs.find({"AddedOn": {"$lte": end_date, '$gte': start_date}, "IsActive": True, "Subject._id": ObjectId(subs_id)})
        return insight

    @staticmethod
    def get_personal_insights():
        json_file = open("app/configuration/pain_level.json")
        response_list = []
        json_data = json.load(json_file)
        try:
            total_subs = mongo_db.db.Subjects.find({"IsActive": True})
            for subs in total_subs:
                subs_id = subs['_id']
                subs_name = subs['Name']

                start_date, end_date = SubjectService.format_dates("Today")
                todays_insight = SubjectService.format_insight_datas(start_date, end_date, subs_id)
                pain_level_today, sleep_today = SubjectService.extract_pain_data(todays_insight, json_data)

                start_date, end_date = SubjectService.format_dates("Weekly")
                weekly_insight = SubjectService.format_insight_datas(start_date, end_date, subs_id)
                pain_level_last_week, sleep_last_week = SubjectService.extract_pain_data(weekly_insight, json_data)

                start_date, end_date = SubjectService.format_dates("Monthly")
                monthly_insight = SubjectService.format_insight_datas(start_date, end_date, subs_id)
                pain_level_last_month, sleep_last_month = SubjectService.extract_pain_data(monthly_insight, json_data)
 
                if (pain_level_today and sleep_today) or (
                    pain_level_last_week and sleep_last_week) or (
                    pain_level_last_month and sleep_last_month):
                    pain_mood_data = {
                        "Subject Name": subs_name,
                        "Values":"Effect of pain in your mood",
                        "Today": pain_level_today if pain_level_today else "",
                        "Last 7 days": pain_level_last_week if pain_level_last_week else "",
                        "Last 30 days": pain_level_last_month if pain_level_last_month else ""
                    }
                    pain_sleep_data = {
                        "Subject Name":subs_name,
                        "Values":"Effect of pain in your sleep",
                        "Today": sleep_today if sleep_today else "",
                        "Last 7 days": sleep_last_week if sleep_last_week else "",
                        "Last 30 days": sleep_last_month if sleep_last_month else ""
                    }
                    response_list.append(pain_mood_data)
                    response_list.append(pain_sleep_data)
            return response_list
        except:
            return []
    

    @staticmethod
    def pain_details(data, user_identity):

        in_date = data['date']
        in_date = (datetime.strptime(in_date, "%m-%d-%Y").astimezone(pytz.utc)).date()
        start_date = datetime.strptime(str(in_date)+" 00", "%Y-%m-%d %H")
        end_date = datetime.strptime(str(in_date)+" 23", "%Y-%m-%d %H")
        query_data = mongo_db.db.Logs.find_one({"DateOfLog": {"$lte": end_date, '$gt': start_date},
                                            "Subject._id": ObjectId(data['subject']), "IsActive": True})

        bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)

        return format_cursor_obj(json.loads(bs))

    @staticmethod
    def pain_details_fetch(data, user_identity):
        if data['from_date']:
            start_date = datetime.strptime(str(data['from_date']), "%m-%d-%Y")
            utc_start_date = start_date.astimezone(pytz.utc).strftime("%m-%d-%Y")
            in_start_date = datetime.strptime(str(utc_start_date) + " 00:00:01", "%m-%d-%Y %H:%M:%S")

        else:
            in_start_date = ""

        if data['to_date']:
            end_date = datetime.strptime(str(data['to_date']), "%m-%d-%Y")
            utc_end_date = end_date.astimezone(pytz.utc).strftime("%m-%d-%Y")
            in_end_date = datetime.strptime(str(utc_end_date) + " 23:59", "%m-%d-%Y %H:%M")
        else:
            in_end_date = ""

        options = CodecOptions(tz_aware=True)
        query_data = mongo_db.db.get_collection('Logs', codec_options=options)\
            .find({"IsActive": True, "DateOfLog": {"$lte": in_end_date, '$gte': in_start_date}})
        all_data = []
        for data in query_data:
            data['Subject Name'] = data['Subject']['Name']
            t = data['DateOfLog'].astimezone()
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
            else:
                data['Pain Level'] = None
            keys = ['Subject', 'IsActive', 'LastUpdatedOn', 'AddedOn', 'Notes', 'BodySide', 'DateOfLog', 'LevelOfPain']
            list(map(data.pop, keys))
            all_data.append(data)
        return all_data

    @staticmethod
    def export_pain_details(data, user_identity):

        if data['from_date']:
            start_date = datetime.strptime(str(data['from_date']), "%m-%d-%Y")
            utc_start_date = start_date.astimezone(pytz.utc).strftime("%m-%d-%Y")
            in_start_date = datetime.strptime(str(utc_start_date) + " 00:00:01", "%m-%d-%Y %H:%M:%S")

        else:
            in_start_date = ""

        if data['to_date']:
            end_date = datetime.strptime(str(data['to_date']), "%m-%d-%Y")
            utc_end_date = end_date.astimezone(pytz.utc).strftime("%m-%d-%Y")
            in_end_date = datetime.strptime(str(utc_end_date) + " 23:59", "%m-%d-%Y %H:%M")
        else:
            in_end_date = ""

        print("in_start_date >>>>", in_start_date, "in_end_date >>>>>>>", in_end_date)

        all_subjects = []
        for subject in data['subject']:
            subject = ObjectId(subject)
            all_subjects.append(subject)

        options = CodecOptions(tz_aware=True)
        query_data = mongo_db.db.get_collection('Logs', codec_options=options)\
            .find({"Subject._id": {"$in": tuple(all_subjects)},
                   "IsActive": True,
                   "DateOfLog": {"$lte": in_end_date, '$gte': in_start_date}})
        all_data = []
        for data in query_data:
            data['Subject Name'] = data['Subject']['Name']
            t = data['DateOfLog'].astimezone()
            print("DateOfLog >>>>>>>>>", data['DateOfLog'], t)

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
            else:
                data['Pain Level'] = None
            keys = ['Subject', 'IsActive', 'LastUpdatedOn', 'AddedOn', 'Notes', 'BodySide', 'DateOfLog', 'LevelOfPain']
            list(map(data.pop, keys))
            all_data.append(data)
        data_file = export_pain_data(all_data)
        return data_file


class RewardRedemptionService:
    @staticmethod
    def list_accumulated_rewards(data, user_identity):
        all_subjects = []
        for subject in data['subject']:
            subject = ObjectId(subject)
            all_subjects.append(subject)
        event_type = data['event_type'] if data['event_type'] else []
        if data['from_date']:
            start_date = datetime.strptime(str(data['from_date']) + " 00:00", "%m-%d-%Y %H:%M")
        else:
            start_date = ""
        if data['to_date']:
            end_date = datetime.strptime(str(data['to_date']) + " 23:59", "%m-%d-%Y %H:%M")
        else:
            end_date = ""
        query_data = list(mongo_db.db.RewardAccumulate.find().sort("AddedOn", -1))
        if all_subjects:
            print("subject")
            query_data = list(mongo_db.db.RewardAccumulate.find({"SubjectId": {"$in": tuple(all_subjects)}}).\
                sort("AddedOn", -1))

        if event_type:
            print("event")
            query_data = list(mongo_db.db.RewardAccumulate.find({"EventType": {"$in": tuple(event_type)}}).\
                sort("AddedOn", -1))

        if all_subjects and event_type:
            print("with event")
            query_data = list(mongo_db.db.RewardAccumulate.find({"EventType": {"$in": tuple(event_type)},
                                                                 "SubjectId": {"$in": tuple(all_subjects)}}). \
                sort("AddedOn", -1))

        if all_subjects and start_date and end_date:
            print("sub date")
            query_data = list(mongo_db.db.RewardAccumulate.find({"AddedOn": {"$lte": end_date, '$gt': start_date},
                                                                 "SubjectId": {"$in": tuple(all_subjects)}}).sort(
                "AddedOn", -1))
        if event_type and start_date and end_date:
            print("event date")
            query_data = list(mongo_db.db.RewardAccumulate.find({"AddedOn": {"$lte": end_date, '$gt': start_date},
                                                                 "EventType": {"$in": tuple(event_type)}}).sort(
                "AddedOn", -1))
        if start_date and end_date:
            print("date")
            query_data = list(mongo_db.db.RewardAccumulate.find({"AddedOn": {"$lte": end_date, '$gt': start_date}}).sort(
                "AddedOn", -1))
        if all_subjects and event_type and start_date and end_date:
            print("all filter")
            query_data = list(mongo_db.db.RewardAccumulate.find({"AddedOn": {"$lte": end_date, '$gt': start_date},
                                                "SubjectId": {"$in": tuple(all_subjects)}, "EventType": {"$in": tuple(event_type)}}).sort("AddedOn", -1))

        all_data = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            all_data.append(val)
        return all_data




