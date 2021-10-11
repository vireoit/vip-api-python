from app.subjects.services import SubjectImportService


class SubjectImportDelegate:
    @staticmethod
    def import_subject_csv_file(file):
        imported_file = SubjectImportService.import_subject_csv_file(file)
        return imported_file

    @staticmethod
    def import_subject_xlsx_file(file):
        imported_file = SubjectImportService.import_subject_xlsx_file(file)
        return imported_file
