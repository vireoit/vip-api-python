from app.subjects.export import export_table_data
from app import mongo_db


class SubjectService:
    @staticmethod
    def export_subjects(data, user_identity):
        data = data.get('export_fields')
        data = tuple(data)
        query_data = list(mongo_db.db.Subjects.find({}, data))
        all_data = []
        for data in query_data:
            all_data.append(data)
        data_file = export_table_data(all_data)
        return data_file

    @staticmethod
    def pain_details(data, user_identity):
        print(data)
        query_data = mongo_db.db.Subjects.find({}, data)
        print(print(query_data))
        print(list(query_data))


