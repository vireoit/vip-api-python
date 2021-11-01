import os
from uuid import uuid4
import pandas as pd
import json
from app import ma, response, mongo_db
from datetime import datetime, timezone
from app.subjects.schemas import SubjectImportSchema
from app.surveys.export import export_table_data
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
import requests
from app.utils.http_service_util import perform_http_request
from app.base_urls import VIP_ADMIN_URL, VIP_BACKEND_URL
from app.utils.mongo_encoder import format_cursor_obj

class SurveyService:
    @staticmethod
    def export_survey_reports(data, parameters):
        try:
            list_of_questions = []
            all_data = []
            survey_id = data.get('survey_id')
            subject_ids = data.get('subject_ids')
            question_list = data.get('question_list')
            for ql in question_list:
                list_of_questions.append(ql['question'])
            query_data = mongo_db.db.Surveys.find({"_id": ObjectId(survey_id), 
            "Patients._id": {"$in": tuple(subject_ids)}, 
            "QuestionsAndAnswers.Question": {"$in": tuple(list_of_questions)}}).sort('CreatedOn', -1)
            for values in query_data:
                bs = dumps(values, json_options=RELAXED_JSON_OPTIONS)
                val = format_cursor_obj(json.loads(bs))
                val['Survey Name'] = val['Name']
                plist = []
                answerlist = []
                for patient in val['Patients']:
                    plist.append(patient['Name'])
                val['Patients Name'] = ', '.join(map(str, plist))
                for qa in val['QuestionsAndAnswers']:
                    val['Question'] = qa['Question']
                    for answers in qa['Answers']:
                        answerlist.append(answers['Answer'])
                val['Answers'] = ', '.join(map(str, answerlist))
                keys = ['_id', 'Product', 'LastUpdatedOn', 'StartDate', 'IsActive', 'EndDate', 'Patients', 'FormProperties',
                'IsSelectedAll', 'Status', 'Frequency', 'SurveyType', 'TimeToComplete', 'TotalInputQuestions', 'QuestionsAndAnswers', 
                'Name']
                list(map(val.pop, keys))
                all_data.append(val)
    
            data_file = export_table_data(all_data)
            return data_file
        except:
            return None
        
        