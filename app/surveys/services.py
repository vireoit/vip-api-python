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
            response_data = perform_http_request(f'{VIP_BACKEND_URL}/api/Surveys/Reports', parameters['authorization'], 
                body=data, request_method="POST")
            is_valid = response_data.get('responseCode') == 200 and response_data.get('data')
            response_list = []
            if is_valid:
                all_data = response_data.get('data')
                all_data = json.load(all_data)
                all_data1 = all_data[:]

                for data in all_data:
                    dict = {
                        'Subject Name': data['subjectName'],
                        'Submitted Date': data['submittedDate'],
                    }
                    for rec in all_data1:
                        if data['subjectName'] == rec['subjectName']:
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
        except:
            return None
        
        