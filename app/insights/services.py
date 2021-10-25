from app import ma, response, mongo_db
from app.utils.mongo_encoder import format_cursor_obj

import json

from datetime import datetime, timedelta, date

from bson.objectid import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS


class PainDetailGraphService:
    @staticmethod
    def pain_details_graph(filters, user_identity):
        subject = filters['subject'] if 'subject' in filters else ""
        param = filters['param'] if 'param' in filters else ""
        all_data = []
        if param == "today":
            date_today = date.today()
            start_date = datetime.strptime(str(date_today) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": ObjectId(subject), "IsActive": True}). \
                              sort("AddedOn", -1))
            if query_data:
                data = query_data[0]
                dict={}
                dict['score'] = data['Percentage']
                dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(dict)
        elif param == "week":
            date_today = date.today()
            week_ago = date_today - timedelta(days=7)
            start_date = datetime.strptime(str(week_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": ObjectId(subject), "IsActive": True}). \
                              sort("AddedOn", -1))
            for data in query_data:
                dict = {}
                dict['score'] = data['Percentage']
                dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(dict)
                subject = data['SubjectId']
                in_date = data['AddedOn'].strftime('%Y-%m-%d')
                for record in query_data:
                    if record['SubjectId'] == subject and record['AddedOn'].strftime('%Y-%m-%d') == in_date:
                        query_data.remove(record)

        elif param == "month":
            date_today = date.today()
            month_ago = date_today - timedelta(days=30)
            start_date = datetime.strptime(str(month_ago) + " 00", "%Y-%m-%d %H")
            end_date = datetime.strptime(str(date_today) + " 23", "%Y-%m-%d %H")
            query_data = list(mongo_db.db.Pegs.find({"AddedOn": {"$lte": end_date, '$gte': start_date},
                                                     "SubjectId": ObjectId(subject), "IsActive": True}). \
                              sort("AddedOn", -1))
            all_data = []
            for data in query_data:
                dict = {}
                dict['score'] = data['Percentage']
                dict['date'] = data['AddedOn'].strftime('%m-%d-%Y')
                all_data.append(dict)
                subject = data['SubjectId']
                in_date = data['AddedOn'].strftime('%Y-%m-%d')
                for record in query_data:
                    if record['SubjectId'] == subject and record['AddedOn'].strftime('%Y-%m-%d') == in_date:
                        query_data.remove(record)

        return all_data



