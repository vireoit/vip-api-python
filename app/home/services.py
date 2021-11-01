from app import ma, response, mongo_db

import json
import re
import pytz
from datetime import date, datetime, timedelta
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from app.utils.mongo_encoder import format_cursor_obj
from bson.codec_options import CodecOptions
from app.utils.http_service_util import perform_http_request
from app.base_urls import VIP_BACKEND_URL

class PegScoreService:
    @staticmethod
    def update_allowed_rewards(data):
        configured_reward = mongo_db.db.Rewards.find_one()
        query_data = mongo_db.db.Subjects.find_one({"_id": ObjectId(data['SubjectId'])})
        print(query_data)
        if configured_reward:
            for data_dict in configured_reward['RewardConfig']:
                if data_dict['eventType'] == "My pain score":
                    dict = {}
                    dict['RewardAccumulated'] = data_dict['points']
                    dict['SubjectId'] = ObjectId(data['SubjectId'])
                    dict['Name'] = query_data['Name']
                    print("dvdbhjdfv")
                    dict['EventType'] = data_dict['eventType']
                    dict['AddedOn'] = datetime.utcnow()
                    create_date = mongo_db.db.RewardAccumulate.insert_one(dict)

    @staticmethod
    def create_peg_score_record(data, user_identity):
        data['AddedOn'] = datetime.utcnow()
        data['SubjectId'] = ObjectId(data['SubjectId'])
        total = 0
        for record in data['QuestionAnswers']:
            total = total+record['value']
        data['Percentage'] = int(total/3)
        data['IsActive'] = True
        create_date = mongo_db.db.Pegs.insert_one(data)
        PegScoreService.update_allowed_rewards(data)
        return create_date

    @staticmethod
    def peg_score_details(data, user_identity):
        query_data = list(mongo_db.db.Pegs.find({"SubjectId": ObjectId(data['subject']), "IsActive": True}).\
            sort("AddedOn", -1))

        bs = dumps(query_data[0], json_options=RELAXED_JSON_OPTIONS)

        return format_cursor_obj(json.loads(bs))


class OnGoingFeedbackService:
    @staticmethod
    def create_on_going_feedback(data, user_identity):
        data['added_on'] = datetime.utcnow()
        data['subject_id'] = ObjectId(data['subject_id'])
        data['feedback'] = int(data['feedback'])
        create_data = mongo_db.db.Feedback.insert_one(data)
        return create_data


class SatisfactionService:
    @staticmethod
    def update_allowed_rewards(data):
        configured_reward = mongo_db.db.Rewards.find_one()
        query_data = mongo_db.db.Subjects.find_one({"_id": ObjectId(data['SubjectId'])})
        if configured_reward:
            for data_dict in configured_reward['RewardConfig']:
                if data_dict['eventType'] == "My satisfaction score":
                    dict = {}
                    dict['RewardAccumulated'] = data_dict['points']
                    dict['SubjectId'] = ObjectId(data['SubjectId'])
                    dict['Name'] = query_data['Name']
                    dict['EventType'] = data_dict['eventType']
                    dict['AddedOn'] = datetime.utcnow()
                    create_date = mongo_db.db.RewardAccumulate.insert_one(dict)

    @staticmethod
    def take_integer_from_string(data):
        if data == "NA":
            return 0
        else:
            return (int(re.search(r'\d+', data).group()))

    @staticmethod
    def create_Satisfaction_score_record(data, user_identity):
        data['AddedOn'] = datetime.utcnow()
        data['SubjectId'] = ObjectId(data['SubjectId'])
        data['IsActive'] = True
        create_date = mongo_db.db.Satisfaction.insert_one(data)
        SatisfactionService.update_allowed_rewards(data)
        return create_date

    @staticmethod
    def satisfaction_score_details(data, user_identity):
        peg_query_data = list(mongo_db.db.Pegs.find({"SubjectId": ObjectId(data['subject']), "IsActive": True}). \
                          sort("AddedOn", -1))
        satisfaction_query_data = list(mongo_db.db.Satisfaction.find({"SubjectId": ObjectId(data['subject']), "IsActive": True}). \
                          sort("AddedOn", -1))

        bs = dumps(satisfaction_query_data[0], json_options=RELAXED_JSON_OPTIONS)

        if peg_query_data and satisfaction_query_data:
            recommendation = SatisfactionService.recommendation(peg_query_data[0], satisfaction_query_data[0])
        else:
            recommendation = "No recommendations"
        satisfaction = format_cursor_obj(json.loads(bs))
        satisfaction['recommendation'] = recommendation
        if peg_query_data:
            satisfaction['peg_score'] = peg_query_data[0]['Percentage']
        else:
            satisfaction['peg_score'] = 0
        return satisfaction


    @staticmethod
    def recommendation(peg_score, satisfaction):
        subject_side_effects = satisfaction['TSQMSideEffects']
        subject_peg_score = peg_score['Percentage']
        subject_satisfaction = satisfaction['TSQMSatisfaction']
        subject_severity = satisfaction['TSQMSeverity']
        recommendation = list(mongo_db.db.Dosings.find({"IsActive": True}))
        for data in recommendation:
            side_effects = SatisfactionService.take_integer_from_string(data['TSQMSideEffects'])
            satisfaction = SatisfactionService.take_integer_from_string(data['TSQMSatisfaction'])
            severity = SatisfactionService.take_integer_from_string(data['TSQMSeverity'])
            peg_score = SatisfactionService.take_integer_from_string(data['PEGScore'])
            if subject_side_effects == side_effects:
                if satisfaction >= subject_satisfaction or satisfaction <= subject_satisfaction:
                    if severity >= subject_severity or severity <= subject_severity:
                        if peg_score >= subject_peg_score or peg_score <= subject_peg_score:
                            return data['Recomendation']['Name']
                        else:
                            return "No recommendations"
                    else:
                        return "No recommendations"
                else:
                    return "No recommendations"
            else:
                return "No recommendations"


class AdminHomeStatisticsService:

    @staticmethod
    def get_total_counts(model, start_date, end_date):
        if model == "Subjects":
            query_data = mongo_db.db.Subjects.find({"AddedOn": {"$lte": start_date, '$gte': end_date}}).count()
        elif model == "Surveys":
            query_data = mongo_db.db.Surveys.find({"CreatedOn": {"$lte": start_date, '$gte': end_date}}).count()
        elif model == "Logs":
            query_data = mongo_db.db.Logs.find({"DateOfLog": {"$lte": start_date, '$gte': end_date}}).count()
        elif model == "EducationalVideos":
            query_data = mongo_db.db.EducationalVideos.find({"PostedOn": {"$lte": start_date, '$gte': end_date}}).count()
        return query_data 

    @staticmethod
    def get_date_details(date_data_one, date_data_two):
        start_date = datetime.strptime(str(date_data_one) + " 23", "%Y-%m-%d %H")
        end_date = datetime.strptime(str(date_data_two) + " 00", "%Y-%m-%d %H")
        return start_date, end_date

    @staticmethod
    def get_percentage_change(current_week_count, last_week_count):
        if current_week_count > last_week_count:
            change_type = "Increase"
            percentage_change = ((current_week_count - last_week_count)/current_week_count)*100
        elif current_week_count < last_week_count:
            change_type = "Decrease"
            percentage_change = ((last_week_count - current_week_count)/last_week_count)*100
        else:
            percentage_change = 0
            change_type = "Unchanged"
        return percentage_change, change_type

    @staticmethod
    def get_admin_home_statistics(parameters):
        response_data = []
        date_today = date.today()
        week_ago = date_today - timedelta(days=7)
        two_week_ago = date_today - timedelta(days=14)
        model = "Subjects"
        start_date, end_date = AdminHomeStatisticsService.get_date_details(date_today, week_ago)
        current_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        start_date, end_date = AdminHomeStatisticsService.get_date_details(week_ago, two_week_ago)
        last_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        percentage_change, change_type = AdminHomeStatisticsService.get_percentage_change(current_week_count, last_week_count)
        response_data.append({
            "key": "patients",
            "percentage_change": percentage_change,
            "count": current_week_count,
            "change": change_type
        })
        model = "Surveys"
        start_date, end_date = AdminHomeStatisticsService.get_date_details(date_today, week_ago)
        current_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        start_date, end_date = AdminHomeStatisticsService.get_date_details(week_ago, two_week_ago)
        last_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        percentage_change, change_type = AdminHomeStatisticsService.get_percentage_change(current_week_count, last_week_count)
        response_data.append({
            "key": "surveys",
            "percentage_change": percentage_change,
            "count": current_week_count,
            "change": change_type
        })
        model = "Logs"
        start_date, end_date = AdminHomeStatisticsService.get_date_details(date_today, week_ago)
        current_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        start_date, end_date = AdminHomeStatisticsService.get_date_details(week_ago, two_week_ago)
        last_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        percentage_change, change_type = AdminHomeStatisticsService.get_percentage_change(current_week_count, last_week_count)
        response_data.append({
            "key": "logs",
            "percentage_change": percentage_change,
            "count": current_week_count,
            "change": change_type
        })
        model = "EducationalVideos"
        start_date, end_date = AdminHomeStatisticsService.get_date_details(date_today, week_ago)
        current_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        start_date, end_date = AdminHomeStatisticsService.get_date_details(week_ago, two_week_ago)
        last_week_count = AdminHomeStatisticsService.get_total_counts(model ,start_date, end_date)
        percentage_change, change_type = AdminHomeStatisticsService.get_percentage_change(current_week_count, last_week_count)
        response_data.append({
            "key": "educational_videos",
            "percentage_change": percentage_change,
            "count": current_week_count,
            "change": change_type
        })     
        return response_data

class AdminHomeGraphService:

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
    def get_admin_home_patients(parameters):
        frequency = parameters.get('frequency')
        all_data = []
        if frequency == "Today":
            start_date, end_date = AdminHomeGraphService.format_dates(frequency)
            query_data = mongo_db.db.Subjects.find({"AddedOn": {"$lte": end_date, '$gte': start_date}}).count()
            dict={}
            dict['patient_count'] = query_data
            dict['date'] = start_date.strftime('%m-%d-%Y')
            all_data.append(dict)

        elif frequency == "Weekly":
            start_date, end_date = AdminHomeGraphService.format_dates(frequency)
            query_data = mongo_db.db.Subjects.find({"AddedOn": {"$lte": end_date, '$gte': start_date}}).sort('AddedOn', -1)
            l1 = []
            for data in query_data:
                dict = {}
                if str(data['AddedOn'].date()) not in l1:
                    l1.append(str(data['AddedOn'].date()))
                    start_date = datetime.strptime(str(data['AddedOn'].date()) + " 00", "%Y-%m-%d %H")
                    end_date = datetime.strptime(str(data['AddedOn'].date()) + " 23", "%Y-%m-%d %H")
                    query_data = mongo_db.db.Subjects.find({"AddedOn": {"$lte": end_date, '$gte': start_date}}).count()
                    dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                    dict['patient_count'] = query_data
                    all_data.append(dict)
               
        elif frequency == "Monthly":
            start_date, end_date = AdminHomeGraphService.format_dates(frequency)
            query_data = mongo_db.db.Subjects.find({"AddedOn": {"$lte": end_date, '$gte': start_date}}).sort('AddedOn', -1)
            l1 = []
            for data in query_data:
                dict = {}
                if str(data['AddedOn'].date()) not in l1:
                    l1.append(str(data['AddedOn'].date()))
                    start_date = datetime.strptime(str(data['AddedOn'].date()) + " 00", "%Y-%m-%d %H")
                    end_date = datetime.strptime(str(data['AddedOn'].date()) + " 23", "%Y-%m-%d %H")
                    query_data = mongo_db.db.Subjects.find({"AddedOn": {"$lte": end_date, '$gte': start_date}}).count()
                    dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                    dict['patient_count'] = query_data
                    all_data.append(dict)
        return all_data

    @staticmethod
    def get_admin_home_treatments(parameters, claims):
        frequency = parameters.get('frequency')
        all_data = []
        subject_id = claims['subject_id']
        if frequency == "Today":
            response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopTreatmentsForOtherUsers?dateCategory=Day&patientId={subject_id}', claims['authorization'], 
            body={}, request_method="GET")
            if response_data_today.get('responseCode') == 200:
                response = response_data_today.get('data')[0:2]
                return response
            return []

        elif frequency == "Weekly":
            response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopTreatmentsForOtherUsers?dateCategory=Week&patientId={subject_id}', claims['authorization'], 
            body={}, request_method="GET")
            if response_data_today.get('responseCode') == 200:
                response = response_data_today.get('data')[0:2]
                return response
            return []
               
        elif frequency == "Monthly":
            response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopTreatmentsForOtherUsers?dateCategory=Month&patientId={subject_id}', claims['authorization'], 
            body={}, request_method="GET")
            if response_data_today.get('responseCode') == 200:
                response = response_data_today.get('data')[0:2]
                return response
            return []

        return all_data

    @staticmethod
    def get_admin_home_surveys(parameters):
        frequency = parameters.get('frequency')
        all_data = []
        if frequency == "Today":
            start_date, end_date = AdminHomeGraphService.format_dates(frequency)
            query_data = mongo_db.db.Surveys.find({"CreatedOn": {"$lte": end_date, '$gte': start_date}}).count()
            dict={}
            dict['survey_count'] = query_data
            dict['date'] = start_date.strftime('%m-%d-%Y')
            all_data.append(dict)

        elif frequency == "Weekly":
            start_date, end_date = AdminHomeGraphService.format_dates(frequency)
            query_data = mongo_db.db.Surveys.find({"CreatedOn": {"$lte": end_date, '$gte': start_date}}).sort('CreatedOn', -1)
            l1 = []
            for data in query_data:
                dict = {}
                if str(data['CreatedOn'].date()) not in l1:
                    l1.append(str(data['CreatedOn'].date()))
                    start_date = datetime.strptime(str(data['CreatedOn'].date()) + " 00", "%Y-%m-%d %H")
                    end_date = datetime.strptime(str(data['CreatedOn'].date()) + " 23", "%Y-%m-%d %H")
                    query_data = mongo_db.db.Surveys.find({"CreatedOn": {"$lte": end_date, '$gte': start_date}}).count()
                    dict['date'] = data['CreatedOn'].strftime('%m-%d-%Y')
                    dict['survey_count'] = query_data
                    all_data.append(dict)
               
        elif frequency == "Monthly":
            start_date, end_date = AdminHomeGraphService.format_dates(frequency)
            query_data = mongo_db.db.Surveys.find({"CreatedOn": {"$lte": end_date, '$gte': start_date}}).sort('CreatedOn', -1)
            l1 = []
            for data in query_data:
                dict = {}
                if str(data['CreatedOn'].date()) not in l1:
                    l1.append(str(data['CreatedOn'].date()))
                    start_date = datetime.strptime(str(data['CreatedOn'].date()) + " 00", "%Y-%m-%d %H")
                    end_date = datetime.strptime(str(data['CreatedOn'].date()) + " 23", "%Y-%m-%d %H")
                    query_data = mongo_db.db.Surveys.find({"CreatedOn": {"$lte": end_date, '$gte': start_date}}).count()
                    dict['date'] = data['CreatedOn'].strftime('%m-%d-%Y')
                    dict['survey_count'] = query_data
                    all_data.append(dict)
        return all_data

    @staticmethod
    def get_admin_home_pain_type(parameters, claims):
        frequency = parameters.get('frequency')
        all_data = []
        subject_id = claims['subject_id']
        if frequency == "Today":
            response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Day&patientId={subject_id}', claims['authorization'], 
            body={}, request_method="GET")
            if response_data_today.get('responseCode') == 200:
                response = response_data_today.get('data')[0:2]
                return response
            return []

        elif frequency == "Weekly":
            response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Week&patientId={subject_id}', claims['authorization'], 
            body={}, request_method="GET")
            if response_data_today.get('responseCode') == 200:
                response = response_data_today.get('data')[0:2]
                return response
            return []
               
        elif frequency == "Monthly":
            response_data_today = perform_http_request(f'{VIP_BACKEND_URL}/api/CommunityInsights/GetTopPainLoggedForOtherUsers?dateCategory=Month&patientId={subject_id}', claims['authorization'], 
            body={}, request_method="GET")
            if response_data_today.get('responseCode') == 200:
                response = response_data_today.get('data')[0:2]
                return response
            return []

        return all_data
