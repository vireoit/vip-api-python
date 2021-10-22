from app import ma, response, mongo_db

import json

from datetime import date, datetime
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from app.utils.mongo_encoder import format_cursor_obj


class PegScoreService:
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
        data['AddedOn'] = datetime.utcnow()
        data['SubjectId'] = ObjectId(data['SubjectId'])
        data['Feedback'] = int(data['Feedback'])
        create_data = mongo_db.db.Feedback.insert_one(data)
        return create_data


class SatisfactionService:
    @staticmethod
    def create_Satisfaction_score_record(data, user_identity):
        data['AddedOn'] = datetime.utcnow()
        data['SubjectId'] = ObjectId(data['SubjectId'])
        data['IsActive'] = True
        create_date = mongo_db.db.Satisfaction.insert_one(data)
        return create_date

    @staticmethod
    def satisfaction_score_details(data, user_identity):
        query_data = list(mongo_db.db.Satisfaction.find({"SubjectId": ObjectId(data['subject']), "IsActive": True}). \
                          sort("AddedOn", -1))

        bs = dumps(query_data[0], json_options=RELAXED_JSON_OPTIONS)

        return format_cursor_obj(json.loads(bs))
