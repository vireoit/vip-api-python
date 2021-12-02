import os
from re import template
from urllib.parse import uses_fragment
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
from app.base_urls import VIP_EMAIL_LINK
from app.exceptions import RedeemedPoint

from statistics import mode
from app.utils.email_service_util import send_email
from flask import render_template


class SubjectImportService:

    @staticmethod
    def add_subject_to_survey(subjects):
        """Add new subject to survey with empty values"""
        try:
            surveys = mongo_db.db.Surveys.find({"IsSelectedAll": True})
            for survey in surveys:
                patients = survey.get("Patients")
                if patients:
                    for subject_id in subjects:
                        subject = mongo_db.db.Subjects.find_one({'_id': subject_id})
                        patient_dict = {"_id": ObjectId(subject["_id"]), "Name": subject["Name"], "Gender": subject["Gender"]}
                        dates_info = patients[0].get("DatesInfo", [])

                        if len(dates_info) > 0:
                            for date_info in dates_info:
                                date_info["SubmittedDate"] = None
                                date_info["TotalFilledInputQuestions"] = 0
                                date_info["CompletionPercent"] = 0
                                date_info["IsCompleted"] = False
                                questions_answers = date_info.get("QuestionsAndAnswers", [])

                                if len(questions_answers) > 0:
                                    for question_answer in questions_answers:
                                        answers = question_answer.get("Answers", [])
                                        if len(answers) > 0:
                                            for answer in answers:
                                                answer["Answer"] = ""
                                                answer["Image"] = ""
                                                answer["Title"] = ""
                                                answer["Description"] = ""

                        patient_dict.update({"DatesInfo": dates_info})
                        mongo_db.db.Surveys.update({"IsSelectedAll": True}, {"$push": {"Patients": patient_dict}}, multi=True)
        except Exception as e:
            print(e)

    @staticmethod
    def format_email_verification_data(inactive_subjects_query, parameters):
        data_list = []
        for sub in inactive_subjects_query:
            data_dict = dict()
            bs = dumps(sub, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            data_dict['email_id'] = val['Email']
            data_dict['name'] = val['Name']
            data_dict['url'] = "https://" + VIP_EMAIL_LINK + "/activation?guid=" + val['_id']
            data_list.append(data_dict)
        return data_list
            
    @staticmethod
    def format_file(data):
        data.columns = data.columns.str.replace(' ', '')
        data.drop_duplicates(subset=['Email'], keep="first", inplace=True)
        data.drop_duplicates(subset=['Phone'], keep="first", inplace=True)
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
            SubjectImportSchema().load({"subjects": repeat_list})
            for item in repeat_list:
                email_id = item['Email']
                phone_no = item['Phone']
                if phone_no and phone_no[0] != "+":
                    item['Phone'] = "+1" +"-("+phone_no[0:3]+")"+" "+phone_no[3:6]+"-"+phone_no[6:]
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": phone_no}]})
                if item_exist and (item_exist['Email'] == email_id or item_exist['Phone'] == phone_no):
                    payload.remove(item)
            for rt in payload:
                rt['ActivatedOn'] = datetime.utcnow()
                rt['AddedOn'] = datetime.utcnow()
                rt['LastUpdatedOn'] = datetime.utcnow()
                rt['MyPreferedDispenseries'] =""
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
                email_list = []
                for imported_subjects in payload:
                    email_list.append(imported_subjects['Email'])

                result = mongo_db.db.Subjects.insert_many(payload)
                created_ids = result.inserted_ids
                SubjectImportService.add_subject_to_survey(created_ids)
                new_subjects_query = mongo_db.db.Subjects.find({"Email": {"$in": tuple(email_list)}}).sort('AddedOn', -1)
                data = SubjectImportService.format_email_verification_data(new_subjects_query, parameters)
                for val in data:
                    context_data = render_template('PatientActivationMail.html', sending_mail=True, data=val)
                    send_email(subject="Activation mail", recipients=[val['email_id']], text_body="" , html_body=context_data)

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
            SubjectImportSchema().load({"subjects": repeat_list})
            for item in repeat_list:
                email_id = item['Email']
                phone_no = item['Phone']
                if phone_no and phone_no[0] != "+":
                    item['Phone'] = "+1" +"-("+phone_no[0:3]+")"+" "+phone_no[3:6]+"-"+phone_no[6:]
                item_exist = mongo_db.db.Subjects.find_one({"$or":[{"Email": email_id}, {"Phone": item['Phone']}]})
                if item_exist:
                    payload.remove(item)
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
                email_list = []
                for imported_subjects in payload:
                    email_list.append(imported_subjects['Email'])

                result = mongo_db.db.Subjects.insert_many(payload)
                created_ids = result.inserted_ids
                SubjectImportService.add_subject_to_survey(created_ids)
                new_subjects_query = mongo_db.db.Subjects.find({"Email": {"$in": tuple(email_list)}}).sort('AddedOn', -1)
                data = SubjectImportService.format_email_verification_data(new_subjects_query, parameters)
                for val in data:
                    context_data = render_template('PatientActivationMail.html', sending_mail=True, data=val)
                    send_email(subject="Activation mail", recipients=[val['email_id']], text_body="" ,html_body=context_data)

            return {"message": "Subject imported successfully", "value": True}
        except Exception as err:
            error = err.messages
            return {"message": "Subject imported failed", "value": False, "error_data": next(iter(error.values()))}


class SubjectService:
    @staticmethod
    def export_subjects(data, user_identity):
        pain_details = SubjectService.pain_details_fetch(data, user_identity)
        user_ratings = data.get('user_ratings')
        ae_logs = data.get('ae_logs')
        if ae_logs and isinstance(ae_logs, bool):
            ae_list = SubjectService.get_ae_logs(data)
        else:
            ae_list = []
        if user_ratings and isinstance(user_ratings, bool):
            feedback_details = SubjectService.get_user_ratings()
        else:
            feedback_details = []
        insights = data.get('personal_insights')
        data = data.get('export_fields')
        if insights and isinstance(insights, bool):
            insights_data = SubjectService.get_personal_insights()
        else:
            insights_data = []
        data = tuple(data)
        query_data = list(mongo_db.db.Subjects.find({"IsDeleted": False, "UserType": "Patient"}, data))
        all_data = []
        for data in query_data:
            all_data.append(data)
        data_file = export_table_data(all_data, pain_details, insights_data, feedback_details, ae_list)
        return data_file
    
    @staticmethod
    def get_user_ratings():
        query_data = mongo_db.db.Feedback.find({"feedback": {"$ne": 0}}).sort("updated_on", -1)
        feedback_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            query_data = mongo_db.db.Subjects.find_one({"_id": ObjectId(val['subject_id'])})
            val['Subject Name'] = query_data['Name']
            val['Reported Date'] = val['added_on'][0:10]
            val['Rating'] = val['feedback']
            val['Feedback'] = val['suggestions'] if 'suggestions' in data else ""
            keys = ['updated_on','added_on', '_id', 'subject_id', 'feedback']
            if 'suggestions' in data:
                keys.append('suggestions')
            list(map(val.pop, keys))
            feedback_list.append(val)
        return feedback_list
    
    @staticmethod
    def get_ae_logs(data):
        if data['ae_from_date']:
            start_date = datetime.strptime(str(data['ae_from_date']) + " 00:00", "%m-%d-%Y %H:%M")
        else:
            start_date = ""
        if data['ae_to_date']:
            end_date = datetime.strptime(str(data['ae_to_date']) + " 23:59", "%m-%d-%Y %H:%M")
        else:
            end_date = ""
        query_data = list(mongo_db.db.AdverseEvent.find({"AddedOn": {"$lte": end_date, '$gt': start_date}}).sort("AddedOn", -1))
        resource_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            val['Subject Name'] = val['Name']
            val['Event Type'] = list_string_to_string(val['EventType'])
            val['Start Date'] = val['StartDate'][0:10]
            val['Reported Date'] = val['AddedOn'][0:10]
            val['Ongoing or not'] = "Yes" if val['IsOngoing'] == True else "No"
            val['Any relation with cannabis product'] = val['IsCannabisProduct']
            val['Any treatment received for the event'] = val['TreatmentInfo']
            keys = ['_id', 'IsOngoing', 'IsCannabisProduct', 'EventType', 'StartDate', 'AddedOn', 'Name',
            'TreatmentInfo', 'SubjectId', 'IsActive']
            list(map(val.pop, keys))
            resource_list.append(val)
        return resource_list

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
        print(query_data)

        bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)

        return format_cursor_obj(json.loads(bs))

    @staticmethod
    def pain_type_list_to_string(pain_type, others):
        if 'Others' in pain_type:
            other_pain = 'Others - ' + others
            pain_type = [sub.replace('Others', other_pain) for sub in pain_type]
        format_data = (';'.join(pain_type))
        return format_data

    @staticmethod
    def sleep_list_to_string(sleep, others):
        if 'Others' in sleep:
            other_pain = 'Others - ' + others
            sleep = [sub.replace('Others', other_pain) for sub in sleep]
        format_data = (';'.join(sleep))
        return format_data

    @staticmethod
    def pain_detail(lop, json_data):
        list_items = [data_dict for data_dict in json_data if str(data_dict["id"]) == lop]
        if len(list_items) > 0:
            list_items = list_items[0]
            pain_def = list_items['id']+", "+list_items['title']
        else:
            pain_def = ""
        return pain_def

    @staticmethod
    def pain_location_list_to_string(pain_location, level_of_pain, json_data):
        i, j = 0, 0
        l = []
        while i < len(pain_location) and j < len(level_of_pain):
            pain = pain_location[i] +"-"+ SubjectService.pain_detail(level_of_pain[j], json_data)
            l.append(pain)
            i += 1
            j += 1
        format_data = (';'.join(l))
        return format_data
    
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
            data['Submitted Date'] = t.strftime('%m/%d/%Y')
            data['Triggers'] = list_string_to_string(data['Triggers']) 
            data['PainType'] = SubjectService.pain_type_list_to_string(data['PainType'], data['PainTypeOthersNotes'])
            data['Sleep'] = SubjectService.sleep_list_to_string(data['Sleep'], data['SleepDisturbNotes'])
            data['Treatments'] = list_string_to_string(data['Treatments'])
            json_file = open("app/configuration/pain_level.json")
            json_data = json.load(json_file)
            data['PainLocation'] = SubjectService.pain_location_list_to_string(data['PainLocation'], data['LevelOfPain'], json_data)
            if data['Medications']:
                feedback = []
                medication = []
                for value in data['Medications']:
                    if value['Feedback']:
                        feedback_string = str(value['Medication']['Name']) + " - "+ str(value['Feedback'])
                        feedback.append(feedback_string)
                    medications = value['Medication']['Name']+" - " + value['Dosage']
                    medication.append(medications)
                data['Medications'] = (", ".join(medication))
                data['Feedback for vireo products'] = (", ".join(feedback))
            else:
                data['Medications'] = None
            keys = ['Subject', 'IsActive', 'LastUpdatedOn', 'AddedOn', 'BodySide', 'DateOfLog', 'LevelOfPain']
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
            data['SleepOthersNotes'] = data.pop('SleepDisturbNotes')
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
            keys = ['Subject', 'IsActive', 'LastUpdatedOn', 'AddedOn', 'BodySide', 'DateOfLog', 'LevelOfPain']
            list(map(data.pop, keys))
            all_data.append(data)
        data_file = export_pain_data(all_data)
        return data_file


class RewardRedemptionService:
    @staticmethod
    def list_accumulated_rewards(data, user_identity, parameters):
        limit_by = parameters.get('limit')
        page = parameters.get("page")
        order_by = -1
        all_subjects = []
        for subject in data['subject']:
            subject = subject
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
        if all_subjects and event_type and start_date and end_date:
            query_data = list(mongo_db.db.RewardAccumulate.find({"AddedOn": {"$lte": end_date, '$gt': start_date},
                                                "SubjectId": {"$in": all_subjects}, "EventType": {"$in": tuple(event_type)}}).sort("AddedOn", -1))
            total_count = 0
        else:
            total_count = mongo_db.db.RewardAccumulate.find().count()

            query_data = list(mongo_db.db.RewardAccumulate.find(). \
                 skip((page - 1) * limit_by).limit(limit_by).sort("AddedOn", order_by).limit(limit_by))

        all_data = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            all_data.append(val)
        return {
                    "results":all_data,
                    "total_count":total_count
        }

    @staticmethod
    def calculate_redemption(data):
        total_reward_accumulated = 0
        total_redeemed_point = 0
        balance_reward = 0
        if data:
            subject = data[0]['SubjectId']
            for data_dict in data:
                total_reward_accumulated = total_reward_accumulated + data_dict['RewardAccumulated']
            redemption = list(mongo_db.db.RedeemedRecord.find({"SubjectId": ObjectId(subject)}))
            if redemption:
                for data_dict in redemption:
                    total_redeemed_point = total_redeemed_point + data_dict['redeemed_points']
            balance_reward = total_reward_accumulated - total_redeemed_point
        return {
            "total_reward_accumulated": total_reward_accumulated,
            "total_redeemed_point": total_redeemed_point,
            "balance_reward": balance_reward
        }

    @staticmethod
    def list_accumulated_reward_redemption(data, user_identity):
        if data['subject']:
            subject = data['subject']
        else:
            subject = ""
        event_type = data['event_type'] if data['event_type'] else []
        redemption_data = {}
        query_data = []
        if subject:
            query_data = list(mongo_db.db.RewardAccumulate.find({"SubjectId": subject}))
            redemption_data = RewardRedemptionService.calculate_redemption(query_data)

        if subject and event_type:
            query_data = list(mongo_db.db.RewardAccumulate.find({"SubjectId": subject, "EventType": {"$in": tuple(event_type)}}))

        all_data = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            all_data.append(val)
        return {
            "reward": all_data,
            "redemption": redemption_data
        }

    @staticmethod
    def reward_redemption(data, user_identity):
        rewards = list(mongo_db.db.RewardAccumulate.find({"SubjectId": data['subject']}))
        redemption_data = RewardRedemptionService.calculate_redemption(rewards)
        if redemption_data['balance_reward'] < data['points']:
            raise RedeemedPoint()
        redemption_data['balance_reward'] = redemption_data['balance_reward'] - data['points']
        subject = mongo_db.db.Subjects.find_one({"_id": ObjectId(data['subject'])})
        dict = {}
        dict['SubjectId'] = ObjectId(data['subject'])
        dict['Name'] = subject['Name']
        dict['AdminId'] = ObjectId(user_identity['unique_name'])
        dict["total_reward_accumulated"] = redemption_data['total_reward_accumulated']
        dict['redeemed_points'] = data['points']
        dict['balance_reward'] = redemption_data['balance_reward']
        dict['AddedOn'] = datetime.utcnow()
        mongo_db.db.RedeemedRecord.insert_one(dict)

    @staticmethod
    def list_reward_redemption(data, user_identity):
        if data['subject']:
            query_data = list(mongo_db.db.RedeemedRecord.find({"SubjectId": ObjectId(data['subject'])}))
        else:
            query_data = []
        all_data = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            all_data.append(val)
        return all_data


class AdverseEventService:
    @staticmethod
    def list_adverse_event(filters, parameters, user_identity):
        limit_by = parameters.get('limit')
        page = parameters.get("page")
        order_by = -1
        all_subjects = []
        if 'subjects' in filters:
            for subject in filters['subjects']:
                subject = ObjectId(subject)
                all_subjects.append(subject)

        if filters['from_date']:
            start_date = datetime.strptime(str(filters['from_date']) + " 00:00", "%m-%d-%Y %H:%M")
        else:
            start_date = ""
        if filters['to_date']:
            end_date = datetime.strptime(str(filters['to_date']) + " 23:59", "%m-%d-%Y %H:%M")
        else:
            end_date = ""

        total_count = mongo_db.db.AdverseEvent.find({}).count()

        query_data = list(mongo_db.db.AdverseEvent.find().skip((page - 1) * limit_by).limit(limit_by).sort("AddedOn",
                                                                                                       order_by).limit(
                limit_by))

        if all_subjects:

            total_count = mongo_db.db.AdverseEvent.find({"SubjectId": {"$in": tuple(all_subjects)}}).count()
            query_data = list(mongo_db.db.AdverseEvent.find({"SubjectId": {"$in": tuple(all_subjects)}}).\
                skip((page - 1) * limit_by).limit(limit_by).sort("AddedOn", order_by).limit(limit_by))

        if all_subjects and start_date and end_date:

            total_count = mongo_db.db.AdverseEvent.find({"SubjectId": {"$in": tuple(all_subjects)}}).count()
            query_data = list(mongo_db.db.AdverseEvent.find({"AddedOn": {"$lte": end_date, '$gt': start_date},
                                                                 "SubjectId": {"$in": tuple(all_subjects)}}).\
                              skip((page - 1) * limit_by).limit(limit_by).sort("AddedOn", order_by).limit(limit_by))

        bs = dumps(query_data, json_options=RELAXED_JSON_OPTIONS)
        resource_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            resource_list.append(val)
        response_data = {
            'adverse_list': resource_list,
            'total_count': total_count
        }
        return response_data

class RatingAndFeedbackDetailsService:
    @staticmethod
    def get_rating_feedback_details(parameters):
        limit_by = parameters.get('limit')
        page = parameters.get("page")
        total_count = mongo_db.db.Feedback.find({"feedback": {"$ne": 0}}).count()
        query_data = mongo_db.db.Feedback.find({"feedback": {"$ne": 0}}).sort("updated_on", -1).skip((page-1) * limit_by).limit(limit_by).limit(limit_by)
        feedback_list = []
        for data in query_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            query_data = mongo_db.db.Subjects.find_one({"_id": ObjectId(val['subject_id'])})
            val['subject_name'] = query_data['Name']
            feedback_list.append(val)
        response_data = {
            'result': feedback_list,
            'total_count': total_count
        }
        return response_data
