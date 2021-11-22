from app.educational.services import EducationalService


class EducationalDelegate:
    @staticmethod
    def educational_video(payload, user_identity):
        response = EducationalService.educational_video(payload, user_identity)
        return response


