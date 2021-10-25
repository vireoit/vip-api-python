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
        if response_data_today.get('responseCode') == 200 and response_data_today['data']:
            for tod in response_data_today['data']:
                val = tod['name']+"("+str(tod['percentage'])+"%"+")"
                today_list.append(val)
        else:
            today_list = []
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Week&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']:
            for week in response_data_weekly['data']:
                val = week['name']+"("+str(week['percentage'])+"%"+")"
                week_list.append(val)
        else:
            week_list = []
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Month&patientId={patient_id}', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']:
            for month in response_data_monthly['data']:
                val = month['name']+"("+str(month['percentage'])+"%"+")"
                month_list.append(val)
        else:
            month_list = []
        return today_list, week_list, month_list

    @staticmethod
    def request_pain_data(patient_id, user_identity):
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInMood?subjectId={patient_id}&frequency=Today', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_today.get('responseCode') != 200 and not response_data_today['data']:
            response_data_today = []
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInMood?subjectId={patient_id}&frequency=Weekly', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_weekly.get('responseCode') != 200 and not response_data_weekly['data']:
            response_data_weekly = []
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInMood?subjectId={patient_id}&frequency=Monthly', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_monthly.get('responseCode') != 200 and not response_data_monthly['data']:
            response_data_monthly = []
        return response_data_today, response_data_weekly, response_data_monthly

    @staticmethod
    def request_sleep_data(patient_id, user_identity):
        response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInSleep?subjectId={patient_id}&frequency=Today', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_today.get('responseCode') == 200 and response_data_today['data']:
            sleep_today = sorted(response_data_today['data'], key=lambda x: x['value'], reverse=True)
        else:
            sleep_today = []
        response_data_weekly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInSleep?subjectId={patient_id}&frequency=Weekly', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_weekly.get('responseCode') == 200 and response_data_weekly['data']:
            sleep_weekly = sorted(response_data_weekly['data'], key=lambda x: x['value'], reverse=True)
        else:
            sleep_weekly = []
        response_data_monthly = perform_http_request(f'{VIP_BACKEND_URL}/api/PersonalInsights/EffectsOfPainInSleep?subjectId={patient_id}&frequency=Monthly', user_identity['authorization'], 
            body={}, request_method="GET")
        if response_data_monthly.get('responseCode') == 200 and response_data_monthly['data']:
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
        all_data.append({
            ' ':'Today', 
            'Top Pain logged by other users': ",".join(top_pain_data_today) if top_pain_data_today else ''
        })
        all_data.append({
            ' ':'Last 7 Days', 
            'Top Pain logged by other users': ",".join(top_pain_data_weekly) if top_pain_data_weekly else ''
        })
        all_data.append({
            ' ':'Last 30 Days', 
            'Top Pain logged by other users': ",".join(top_pain_data_monthly) if top_pain_data_monthly else ''
        })
        data_file = export_table_data_community(all_data)
        return data_file
      


class PainDetailGraphService:
    @staticmethod
    def pain_details_graph(filters, user_identity):
        subject = filters['subject'] if 'subject' in filters else ""
        param = filters['param'] if 'param' in filters else ""
        all_data = []
        if param == "today":
            date_today = date.today()
            start_date = datetime.strptime(str(date_today) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": ObjectId(subject), "IsActive": True}). \
                              sort("AddedOn", -1))

            if query_data:
                data = query_data[0]
                dict={}
                dict['score'] = data['Percentage']
                dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(dict)

            data = query_data[0]
            dict={}
            dict['score'] = data['Percentage']
            dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
            all_data.append(dict)

        elif param == "week":
            date_today = date.today()
            week_ago = date_today - timedelta(days=7)
            start_date = datetime.strptime(str(week_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": ObjectId(subject), "IsActive": True}). \
                              sort("AddedOn", -1))
            for data in query_data:
                dict = {}
                dict['score'] = data['Percentage']
                dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(dict)
                subject = data['SubjectId']
                in_date = data['AddedOn'].strftime('%Y-%m-%d')
                for record in query_data:
                    if record['SubjectId'] == subject and record['AddedOn'].strftime('%Y-%m-%d') == in_date:
                        query_data.remove(record)

        elif param == "month":
            date_today = date.today()
            month_ago = date_today - timedelta(days=30)
            start_date = datetime.strptime(str(month_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": ObjectId(subject), "IsActive": True}). \
                              sort("AddedOn", -1))
            all_data = []
            for data in query_data:
                dict = {}
                dict['score'] = data['Percentage']
                dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(dict)
                subject = data['SubjectId']
                in_date = data['AddedOn'].strftime('%Y-%m-%d')
                for record in query_data:
                    if record['SubjectId'] == subject and record['AddedOn'].strftime('%Y-%m-%d') == in_date:
                        query_data.remove(record)

        return all_data

