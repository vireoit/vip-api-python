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
