from app.subjects.services import SubjectService


class SubjectDelegate:
    @staticmethod
    def export_subjects(filters, user_identity):
        program = SubjectService.export_subjects(filters, user_identity)
        return program