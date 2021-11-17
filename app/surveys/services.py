import os
from uuid import uuid4
import pandas as pd
import json
from app import ma, response, mongo_db
from datetime import datetime, timezone, timedelta
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

        in_survey_id, in_subject_ids, in_question_list = SurveyService.cleaned_inputs(data)
        try:
            # response_data = perform_http_request(f'{VIP_BACKEND_URL}/api/Surveys/Reports', parameters['authorization'],
            #     body=data, request_method="POST")
            # is_valid = response_data.get('responseCode') == 200 and response_data.get('data')
            response_list = []

            all_data = SurveyService.get_survey_questions(in_survey_id, in_subject_ids, in_question_list)
            if all_data:
                # all_data = response_data.get('data')
                all_data1 = all_data[:]

                for data in all_data:
                    submitted_date = data['submittedDate'] + timedelta(hours=5, minutes=30)
                    dict = {
                        'Subject Name': data['subjectName'],
                        'Submitted Date': submitted_date.strftime("%d/%m/%Y"),
                        data['question']: data['answer']
                    }
                    for rec in all_data1:
                        if data['subjectName'] == rec['subjectName'] and data['submittedDate'].date() == rec['submittedDate'].date():
                            dict1 = {
                                rec['question']: rec['answer']
                            }
                            dict.update(dict1)
                    response_list.append(dict)
                new_response_set = set()
                new_response_list = []
                for data in response_list:
                    new_tuple = tuple(data.items())
                    if new_tuple not in new_response_set:
                        new_response_set.add(new_tuple)
                        new_response_list.append(data)
            data_file = export_table_data(new_response_list)
            return data_file
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_survey_questions(in_survey_id, in_subject_ids, in_question_list):

        survey_sub_query = {'_id': {'$in': in_survey_id}}
        patient_sub_query = {'Patients._id': {'$in': in_subject_ids}}

        aggr_data = mongo_db.db.Surveys.aggregate([
            {"$unwind": "$Patients"},
            {"$unwind": "$Patients.DatesInfo"},
            {"$unwind": "$Patients.DatesInfo.QuestionsAndAnswers"},
            {"$unwind": "$Patients.DatesInfo.QuestionsAndAnswers.Answers"},
            {"$match": survey_sub_query},
            {"$match": patient_sub_query},
            {"$match": {"Patients.DatesInfo.QuestionsAndAnswers.Answers.Answer": {"$nin": ['null', ""]}}},

            {"$match": {"Patients.DatesInfo.QuestionsAndAnswers.Question": {'$in': in_question_list}}},

            {"$project": {'Name':1, 'Patients.Name': 1, 'Patients.DatesInfo.QuestionsAndAnswers.Answers': 1, 'Patients._id': 1,
                          "Patients.DatesInfo.QuestionsAndAnswers.Question": 1, "Patients.DatesInfo.SubmittedDate": 1}},

            {"$group": {"_id": "$Patients.Name",
                        "data": {"$push": {"question": "$Patients.DatesInfo.QuestionsAndAnswers.Question",
                                           "answer": "$Patients.DatesInfo.QuestionsAndAnswers.Answers.Answer",
                                           "submittedDate": "$Patients.DatesInfo.SubmittedDate",
                                           "surveyName": "$Name",
                                           "subjectName": "$Patients.Name", "subject_id": "$Patients._id"}}
                        }}])

        data = list(aggr_data)
        new_list = list()
        for data_dict in data:
            new_list.extend(data_dict["data"])
        return new_list

    @staticmethod
    def cleaned_inputs(payload):

        in_survey_id = [ObjectId(survey_id) for survey_id in payload.get("survey_id")]
        in_subject_ids = [ObjectId(subject_id) for subject_id in payload.get("subject_ids")]
        in_question_list = [data_dict['question'] for data_dict in payload.get("question_list") if data_dict.get('question')]

        return in_survey_id, in_subject_ids, in_question_list


