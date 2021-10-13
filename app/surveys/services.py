import os
from uuid import uuid4
import pandas as pd
import json
from app import ma, response, mongo_db
from datetime import datetime, timezone
from app.subjects.schemas import SubjectImportSchema
from app.surveys.export import export_table_data
from bson.objectid import ObjectId
import requests
from app.utils.http_service_util import perform_http_request
from app.base_urls import VIP_ADMIN_URL

class SurveyService:
    @staticmethod
    def export_survey_reports(data, parameters):
        try:
            response_data = perform_http_request(f'{VIP_ADMIN_URL}/api/Surveys/Reports', parameters['authorization'], 
                body=data, request_method="POST")
            if response_data.get('responseCode') == 200:
                all_data = response_data.get('data')
            else:
                all_data = []
            data_file = export_table_data(all_data)
            return data_file
        except:
            return None
        
        