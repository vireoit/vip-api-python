from app import ma, response, mongo_db

import json
import re

from datetime import date, datetime
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from app.utils.mongo_encoder import format_cursor_obj


class PegScoreService:
    @staticmethod
    def update_allowed_rewards(data):
        configured_reward = mongo_db.db.Rewards.find_one()
        query_data = mongo_db.db.Subjects.find_one({"_id": ObjectId(data['SubjectId'])})
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
        if query_data[0]['AddedOn'] >= datetime.utcnow():

            bs = dumps(query_data[0], json_options=RELAXED_JSON_OPTIONS)
            peg_data = format_cursor_obj(json.loads(bs))
        else:
            peg_data = {}
        return peg_data


class OnGoingFeedbackService:
    @staticmethod
    def create_on_going_feedback(data, user_identity):
        data['AddedOn'] = datetime.utcnow()
        data['SubjectId'] = ObjectId(data['SubjectId'])
        data['Feedback'] = int(data['Feedback'])
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

        created_date = satisfaction_query_data[0]
        if created_date['AddedOn'] >= datetime.utcnow():
            bs = dumps(satisfaction_query_data[0], json_options=RELAXED_JSON_OPTIONS)
            satisfaction = format_cursor_obj(json.loads(bs))
        else:
            satisfaction = {}

        if peg_query_data and satisfaction_query_data:
            recommendation = SatisfactionService.recommendation(peg_query_data[0], satisfaction_query_data[0])
        else:
            recommendation = "No recommendations"

        if satisfaction:
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




