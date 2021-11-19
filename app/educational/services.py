from app import ma, response, mongo_db
from app.utils.mongo_encoder import format_cursor_obj
from app.utils.email_service_util import send_email

import json

from datetime import datetime, timedelta, date
from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from flask import render_template


class EducationalService:
    @staticmethod
    def educational_video(payload, user_identity):
        educational_name = payload.get("educational_name")
        educational_video = payload.get("educational_video")
        thumb_image_path = payload.get("thumb_image_path")
        educational_id = payload.get("educational_id")
        data = list(mongo_db.db.EducationalVideos.find({"SubjectList.IsMailSend": False, "_id": ObjectId(educational_id)}))
        # print(data)
        if data:
            subject = [subject['SubjectList'] for subject in data]
            subject_ids = [data['_id'] for data in subject[0]]
            data = list(mongo_db.db.Subjects.find({"_id": {"$in": subject_ids}}))
            for data_dict in data:
                data_dict['educational_name'] = educational_name
                data_dict['educational_video'] = educational_video
                data_dict['thumb_image_path'] = thumb_image_path
                html_body = render_template('educational_video.html', sending_mail=True, context_data=data_dict)
                subject = "Educational Campaign"
                print(data_dict['Email'])
                send_email(subject, sender="vip@tangentia.com", recipients=[data_dict['Email']], text_body="", html_body=html_body)
