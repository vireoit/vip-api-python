from app.subjects.export import export_table_data


class SubjectService:
    @staticmethod
    def export_subjects(filters, user_identity):
        export_table_data(data)