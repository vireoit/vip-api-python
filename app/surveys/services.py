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
            all_data_list = []
            if is_valid:
                all_data = response_data.get('data')
                dict={}
                for data in all_data:
                    dict['Subject Name'] = data['subjectName']
                    dict['Submitted Date'] = data['submittedDate']
                    dict[data['question']] = data['answer']
                    response_list.append(dict)
                response_dict = {k:v for x in response_list for k,v in x.items()}
                all_data_list.append(response_dict)
            data_file = export_table_data(all_data_list)
            return data_file
        except:
            return None
        
        