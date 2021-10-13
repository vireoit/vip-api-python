from app.subjects.services import SubjectImportService, SubjectService, AdminListService


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

class AdminListDelegate:
    @staticmethod
    def get_admin_list(parameters):
        data = AdminListService.get_admin_list(parameters)
        return data
        