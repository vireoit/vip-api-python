from bson import is_valid
from app import ma, response, mongo_db
from app.utils.mongo_encoder import format_cursor_obj

import json

from datetime import datetime, timedelta, date

from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

import os
from re import T
import pandas as pd
import json
import pytz

from uuid import uuid4
from datetime import datetime, timezone, date, timedelta
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS

from app import ma, response, mongo_db
from app.utils.mongo_encoder import format_cursor_obj
from app.utils.data_format_service_util import list_string_to_string
from bson.objectid import ObjectId
from app.insights.export import export_table_data_community, export_table_data_personal
from statistics import mode
from app.utils.http_service_util import perform_http_request
from app.base_urls import VIP_BACKEND_URL


class InsightService:
    @staticmethod
    def request_others_top_pain_data(patient_id, user_identity):
        today_list = []
        week_list = []
        month_list = []
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Day&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_today.get('responseCode') == 200 and response_data_today['data']
        if is_valid:
            for tod in response_data_today['data']:
                val = tod['name']+"("+str(tod['percentage'])+"%"+")"
                today_list.append(val)
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Week&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']
        if is_valid:
            for week in response_data_weekly['data']:
                val = week['name']+"("+str(week['percentage'])+"%"+")"
                week_list.append(val)
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Month&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']
        if is_valid:
            for month in response_data_monthly['data']:
                val = month['name']+"("+str(month['percentage'])+"%"+")"
                month_list.append(val)
        return today_list, week_list, month_list

    @staticmethod
    def request_others_top_treatment_data(patient_id, user_identity):
        today_list = []
        week_list = []
        month_list = []
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopTreatmentsForOtherUsers?dateCategory=Day&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_today.get('responseCode') == 200 and response_data_today['data']
        if is_valid:
            for tod in response_data_today['data']:
                val = tod['name']+"("+str(tod['percentage'])+"%"+")"
                today_list.append(val)
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopTreatmentsForOtherUsers?dateCategory=Week&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']
        if is_valid:
            for week in response_data_weekly['data']:
                val = week['name']+"("+str(week['percentage'])+"%"+")"
                week_list.append(val)
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopTreatmentsForOtherUsers?dateCategory=Month&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']
        if is_valid:
            for month in response_data_monthly['data']:
                val = month['name']+"("+str(month['percentage'])+"%"+")"
                month_list.append(val)
        return today_list, week_list, month_list

    @staticmethod
    def request_others_top_pain_in_sleep_data(patient_id, user_identity):
        today_list = []
        week_list = []
        month_list = []
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetPainEffectSleepForOtherUsers?dateCategory=Day&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_today.get('responseCode') == 200 and response_data_today['data']
        if is_valid:
            for tod in response_data_today['data']:
                val = tod['name']+"("+str(tod['percentage'])+"%"+")"
                today_list.append(val)
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetPainEffectSleepForOtherUsers?dateCategory=Week&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']
        if is_valid:
            for week in response_data_weekly['data']:
                val = week['name']+"("+str(week['percentage'])+"%"+")"
                week_list.append(val)
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetPainEffectSleepForOtherUsers?dateCategory=Month&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']
        if is_valid:
            for month in response_data_monthly['data']:
                val = month['name']+"("+str(month['percentage'])+"%"+")"
                month_list.append(val)
        return today_list, week_list, month_list

    def request_others_gel_feedback_data(patient_id, user_identity):
        today_list = []
        week_list = []
        month_list = []
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetFeedbackOtherUsers?dateCategory=Day&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_today.get('responseCode') == 200 and response_data_today['data']
        if is_valid:
            for tod in response_data_today['data']:
                val = tod['name']+"("+str(tod['percentage'])+"%"+")"
                today_list.append(val)
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetFeedbackOtherUsers?dateCategory=Week&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']
        if is_valid:
            for week in response_data_weekly['data']:
                val = week['name']+"("+str(week['percentage'])+"%"+")"
                week_list.append(val)
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetFeedbackOtherUsers?dateCategory=Month&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']
        if is_valid:
            for month in response_data_monthly['data']:
                val = month['name']+"("+str(month['percentage'])+"%"+")"
                month_list.append(val)
        return today_list, week_list, month_list

    @staticmethod
    def request_pain_data(patient_id, user_identity):
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInMood?subjectId={patient_id}&frequency=Today', user_identity['authorization'], 
            body={}, request_method="GET")
        is_invalid = response_data_today.get('responseCode') != 200 and not response_data_today['data']
        if is_invalid:
            response_data_today = []
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInMood?subjectId={patient_id}&frequency=Weekly', user_identity['authorization'], 
            body={}, request_method="GET")
        is_invalid = response_data_weekly.get('responseCode') != 200 and not response_data_weekly['data']
        if is_invalid:
            response_data_weekly = []
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInMood?subjectId={patient_id}&frequency=Monthly', user_identity['authorization'], 
            body={}, request_method="GET")
        is_invalid = response_data_monthly.get('responseCode') != 200 and not response_data_monthly['data']
        if is_invalid:
            response_data_monthly = []
        return response_data_today, response_data_weekly, response_data_monthly

    @staticmethod
    def request_sleep_data(patient_id, user_identity):
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInSleep?subjectId={patient_id}&frequency=Today', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_today.get('responseCode') == 200 and response_data_today['data']
        if is_valid:
            sleep_today = sorted(response_data_today['data'], key=lambda x: x['value'], reverse=True)
        else:
            sleep_today = []
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInSleep?subjectId={patient_id}&frequency=Weekly', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']
        if is_valid:
            sleep_weekly = sorted(response_data_weekly['data'], key=lambda x: x['value'], reverse=True)
        else:
            sleep_weekly = []
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInSleep?subjectId={patient_id}&frequency=Monthly', user_identity['authorization'], 
            body={}, request_method="GET")
        is_valid = response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']
        if is_valid:
            sleep_monthly = sorted(response_data_monthly['data'], key=lambda x: x['value'], reverse=True)
        else:
            sleep_monthly = []
        return sleep_today, sleep_weekly, sleep_monthly

    @staticmethod
    def export_personal_insights(parameters, user_identity): 
        patient_id= parameters.get('patient_id')
        all_data = []
        pain_data_today, pain_data_weekly, pain_data_monthly = InsightService.request_pain_data(patient_id, user_identity)
        sleep_data_today, sleep_data_weekly, sleep_data_monthly = InsightService.request_sleep_data(patient_id, user_identity)
        all_data.append({
            ' ':'Today', 
            'Effect of Pain in your mood': pain_data_today['data']['moodName'] if pain_data_today else '', 
            'Effect of pain in your sleep': sleep_data_today[0]['key'] if sleep_data_today else ''
        })
        all_data.append({
            ' ':'Last 7 Days', 
            'Effect of Pain in your mood': pain_data_weekly['data']['moodName'] if pain_data_weekly else '', 
            'Effect of pain in your sleep': sleep_data_weekly[0]['key'] if sleep_data_weekly else ''
        })
        all_data.append({
            ' ':'Last 30 Days', 
            'Effect of Pain in your mood': pain_data_monthly['data']['moodName'] if pain_data_monthly else '', 
            'Effect of pain in your sleep': sleep_data_monthly[0]['key'] if sleep_data_monthly else ''
        })
        data_file = export_table_data_personal(all_data)
        return data_file


    @staticmethod
    def export_community_insights(parameters, user_identity):
        patient_id= parameters.get('patient_id')
        all_data = []
        top_pain_data_today, top_pain_data_weekly, top_pain_data_monthly = InsightService.request_others_top_pain_data(patient_id, user_identity)
        top_treatment_today, top_treatment_weekly, top_treatment_monthly = InsightService.request_others_top_treatment_data(patient_id, user_identity)
        pain_effect_sleep_today, pain_effect_sleep_weekly, pain_effect_sleep_monthly = InsightService.request_others_top_pain_in_sleep_data(patient_id, user_identity)
        capsule_feedback_today, capsule_feedback_weekly, capsule_feedback_monthly = InsightService.request_others_gel_feedback_data(patient_id, user_identity)

        all_data.append({
            ' ':'Today', 
            'Top Pain logged by other users': ",".join(top_pain_data_today) if top_pain_data_today else '',
            'Top treatment logged by other users': ",".join(top_treatment_today) if top_treatment_today else '',
            'Effect of pain in other users sleep': ",".join(pain_effect_sleep_today) if pain_effect_sleep_today else '',
            'Soft - Gel capsule feedback from other users': ",".join(capsule_feedback_today) if capsule_feedback_today else ''
        })

        all_data.append({
            ' ':'Last 7 Days', 
            'Top Pain logged by other users': ",".join(top_pain_data_weekly) if top_pain_data_weekly else '',
            'Top treatment logged by other users': ",".join(top_treatment_weekly) if top_treatment_weekly else '',
            'Effect of pain in other users sleep': ",".join(pain_effect_sleep_weekly) if pain_effect_sleep_weekly else '',
            'Soft - Gel capsule feedback from other users': ",".join(capsule_feedback_weekly) if capsule_feedback_weekly else ''
        })
        all_data.append({
            ' ':'Last 30 Days', 
            'Top Pain logged by other users': ",".join(top_pain_data_monthly) if top_pain_data_monthly else '',
            'Top treatment logged by other users': ",".join(top_treatment_monthly) if top_treatment_monthly else '',
            'Effect of pain in other users sleep': ",".join(pain_effect_sleep_monthly) if pain_effect_sleep_monthly else '',
            'Soft - Gel capsule feedback from other users': ",".join(capsule_feedback_monthly) if capsule_feedback_monthly else ''
        })
        data_file = export_table_data_community(all_data)
        return data_file


    @staticmethod
    def create_adverse_event(data, user_identity):
        data['StartDate'] = datetime.strptime(str(data['StartDate']), "%Y-%m-%d")
        data['AddedOn'] = datetime.utcnow()
        data['IsActive'] = True
        data['SubjectId'] = ObjectId(data['SubjectId'])
        query_data = mongo_db.db.Subjects.find_one({"_id": ObjectId(data['SubjectId'])})
        data['Name'] = query_data['Name']
        create_data = mongo_db.db.AdverseEvent.insert_one(data)


class PainDetailGraphService:
    @staticmethod
    def pain_details_graph(filters, user_identity):
        subject = ObjectId(filters['subject']) if 'subject' in filters else ""
        if subject != ObjectId(user_identity["unique_name"]):
            subject = ""
        param = filters['param'] if 'param' in filters else ""
        all_data = []
        if param == "today":
            date_today = date.today()
            start_date = datetime.strptime(str(date_today) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": subject, "IsActive": True}). \
                              sort("AddedOn", -1))

            if query_data:
                data = query_data[0]
                data_dict={}
                data_dict['score'] = data['Percentage']
                data_dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(data_dict)

        elif param == "week":
            date_today = date.today()
            week_ago = date_today - timedelta(days=7)
            start_date = datetime.strptime(str(week_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": subject, "IsActive": True}). \
                              sort("AddedOn", 1))
            data_dict = {}
            for data in query_data:
                data_dict.update({data['AddedOn'].strftime('%m-%d-%Y'): data['Percentage']})
            dict_data = dict(sorted(data_dict.items(), key=lambda item: item[0], reverse=True))
            for i,j in dict_data.items():
                new_dict = {}
                new_dict['score'] = j
                new_dict['date'] = i
                all_data.append(new_dict)

        elif param == "month":
            date_today = date.today()
            month_ago = date_today - timedelta(days=30)
            start_date = datetime.strptime(str(month_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": subject, "IsActive": True}). \
                              sort("AddedOn", -1))
            data_dict = {}
            for data in query_data:
                data_dict.update({data['AddedOn'].strftime('%m-%d-%Y'): data['Percentage']})
            dict_data = dict(sorted(data_dict.items(), key=lambda item: item[0], reverse=True))
            for i, j in dict_data.items():
                new_dict = {}
                new_dict['score'] = j
                new_dict['date'] = i
                all_data.append(new_dict)

        return all_data


class InsightJournalService:
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
    def format_journal_datas(start_date, end_date, patient_id):

        journal_list = []
        medication_journal_list = []
        start_date = datetime.strftime(start_date, "%m-%d-%Y")
        start_date = datetime.strptime(str(start_date), "%m-%d-%Y")
        utc_start_date = start_date.astimezone(pytz.utc).strftime("%m-%d-%Y")
        in_start_date = datetime.strptime(str(utc_start_date) + " 00:00:01", "%m-%d-%Y %H:%M:%S")

        end_date = datetime.strftime(end_date, "%m-%d-%Y")
        end_date = datetime.strptime(str(end_date), "%m-%d-%Y")
        utc_end_date = end_date.astimezone(pytz.utc).strftime("%m-%d-%Y")
        in_end_date = datetime.strptime(str(utc_end_date) + " 23:59:59", "%m-%d-%Y %H:%M:%S")

        journal_data = mongo_db.db.Journals.find({"JournalDate": {"$lte": in_end_date, '$gte': in_start_date},
                                                                              "Patient._id": ObjectId(patient_id), "IsActive": True})
        medication_journal_data = mongo_db.db.MedicationJournals.find({"MedicationJournalDate": {"$lte": in_end_date, '$gte': in_start_date},
                                                                              "Patient._id": ObjectId(patient_id), "IsActive": True})
        for data in journal_data:
                bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
                val = format_cursor_obj(json.loads(bs))
                del val['Patient']
                journal_list.append(val)

        for data in medication_journal_data:
            bs = dumps(data, json_options=RELAXED_JSON_OPTIONS)
            val = format_cursor_obj(json.loads(bs))
            del val['Patient']
            medication_journal_list.append(val)
        return journal_list, medication_journal_list

    @staticmethod
    def get_insight_journal_list(parameters):
        patient_id = parameters.get('patient_id')
        if parameters.get('frequency') == "Today":
            start_date, end_date = InsightJournalService.format_dates(frequency=parameters.get('frequency'))
            journal_list, medication_journal_list = InsightJournalService.format_journal_datas(start_date, end_date, patient_id)
            all_data = {
                "journals": journal_list,
                "medication_journals": medication_journal_list
            }
        elif parameters.get('frequency') == "Weekly":
            start_date, end_date = InsightJournalService.format_dates(frequency=parameters.get('frequency'))
            journal_list, medication_journal_list = InsightJournalService.format_journal_datas(start_date, end_date, patient_id)
            all_data = {
                "journals": journal_list,
                "medication_journals": medication_journal_list
            }
        elif parameters.get('frequency') == "Monthly":
            start_date, end_date = InsightJournalService.format_dates(frequency=parameters.get('frequency'))
            journal_list, medication_journal_list = InsightJournalService.format_journal_datas(start_date, end_date, patient_id)
            all_data = {
                "journals": journal_list,
                "medication_journals": medication_journal_list
            }
        return all_data
