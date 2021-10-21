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
from app.insights.export import export_table_data_personal


class InsightService:
    @staticmethod
    def extract_pain_data(query_data, json_data):
        query_list = list(query_data)
        sleep = query_list[0]['Sleep']
        sum = 0
        for data in query_list:
            sum = sum + int(data['LevelOfPain'][0])    
        lop = sum//len(query_list)
        lop_list = list(str(lop))
        for data_dict in json_data:
            if str(data_dict["id"]) in lop_list:
                pain_level = data_dict['title']    
        return pain_level, sleep[0]

    @staticmethod
    def extract_dates():
        today_start = datetime.strptime(datetime.utcnow().strftime("%m-%d-%Y") + " 00", "%m-%d-%Y %H")
        seven_day = (datetime.utcnow() - timedelta(days=7)).date().strftime("%m-%d-%Y")
        seven_day_start = datetime.strptime(seven_day + " 00", "%m-%d-%Y %H")
        thirty_day = (datetime.utcnow() - timedelta(days=30)).date().strftime("%m-%d-%Y")
        thirty_day_start = datetime.strptime(thirty_day + " 00", "%m-%d-%Y %H")
        today_end = datetime.strptime(datetime.utcnow().strftime("%m-%d-%Y") + " 23", "%m-%d-%Y %H")
        return today_end, today_start, thirty_day_start, seven_day_start

    @staticmethod
    def export_personal_insights(parameters, user_identity):        
        today_end, today_start, thirty_day_start, seven_day_start = InsightService.extract_dates()
        print(today_end, today_start, thirty_day_start, seven_day_start)
        query_data_todays = mongo_db.db.Logs.find({"IsActive": True, "DateOfLog": {"$lte": today_end, '$gte': today_start}})
        query_data_seven_days = mongo_db.db.Logs.find({"IsActive": True, "DateOfLog": {"$lte": today_end, '$gte': seven_day_start}})
        query_data_thirty_days = mongo_db.db.Logs.find({"IsActive": True, "DateOfLog": {"$lte": today_end, '$gte': thirty_day_start}})
        json_file = open("app/configuration/pain_level.json")
        json_data = json.load(json_file)
        pain_level_today, sleep_today = InsightService.extract_pain_data(query_data_todays, json_data)
        pain_level_last_week, sleep_last_week = InsightService.extract_pain_data(query_data_seven_days, json_data)
        pain_level_last_month, sleep_last_month = InsightService.extract_pain_data(query_data_thirty_days, json_data)
        all_data = []
        all_data.append({' ':'Today', 'Effect of Pain in your mood': pain_level_today, 'Effect of pain in your sleep': sleep_today})
        all_data.append({' ':'Last 7 Days', 'Effect of Pain in your mood': pain_level_last_week, 'Effect of pain in your sleep': sleep_last_week})
        all_data.append({' ':'Last 30 Days', 'Effect of Pain in your mood': pain_level_last_month, 'Effect of pain in your sleep': sleep_last_month})
        data_file = export_table_data_personal(all_data)
        return data_file

    @staticmethod
    def export_community_insights(parameters, user_identity):
        pass
