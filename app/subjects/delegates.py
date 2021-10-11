from app.subjects.services import SubjectImportService


class SubjectImportDelegate:
    @staticmethod
    def import_subject_csv_file(file):
        response = SubjectImportService.import_subject_csv_file(file)
        return response

    @staticmethod
    def import_subject_xlsx_file(file):
        response = SubjectImportService.import_subject_xlsx_file(file)
        return response
