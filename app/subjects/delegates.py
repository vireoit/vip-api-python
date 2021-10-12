from app.subjects.services import SubjectImportService, SubjectService


class SubjectImportDelegate:
    @staticmethod
    def import_subject_csv_file(file):
        response = SubjectImportService.import_subject_csv_file(file)
        return response

    @staticmethod
    def import_subject_xlsx_file(file):
        response = SubjectImportService.import_subject_xlsx_file(file)
        return response


class SubjectDelegate:
    @staticmethod
    def export_subjects(filters, user_identity):
        data_file = SubjectService.export_subjects(filters, user_identity)
        return data_file

    @staticmethod
    def pain_details(filters, user_identity):
        data = SubjectService.pain_details(filters, user_identity)
        return data

    @staticmethod
    def export_pain_details(filters, user_identity):
        data = SubjectService.export_pain_details(filters, user_identity)
        return data

