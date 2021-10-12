from app.subjects.services import SubjectService


class SubjectDelegate:
    @staticmethod
    def export_subjects(filters, user_identity):
        data_file = SubjectService.export_subjects(filters, user_identity)
        return data_file

    @staticmethod
    def pain_details(filters, user_identity):
        data = SubjectService.pain_details(filters, user_identity)
        return data