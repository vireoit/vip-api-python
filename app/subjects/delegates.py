from app.subjects.services import SubjectImportService, SubjectService, RewardRedemptionService, AdverseEventService


class SubjectImportDelegate:
    @staticmethod
    def import_subject_csv_file(file, parameters):
        response = SubjectImportService.import_subject_csv_file(file, parameters)
        return response

    @staticmethod
    def import_subject_excel_file(file, parameters):
        response = SubjectImportService.import_subject_excel_file(file, parameters)
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


class RewardRedemption:
    @staticmethod
    def list_accumulated_rewards(filters, user_identity):
        data = RewardRedemptionService.list_accumulated_rewards(filters, user_identity)
        return data

    @staticmethod
    def list_accumulated_reward_redemption(filters, user_identity):
        data = RewardRedemptionService.list_accumulated_reward_redemption(filters, user_identity)
        return data

    @staticmethod
    def reward_redemption(payload, user_identity):
        data = RewardRedemptionService.reward_redemption(payload, user_identity)
        return data

    @staticmethod
    def list_reward_redemption(filters, user_identity):
        data = RewardRedemptionService.list_reward_redemption(filters, user_identity)
        return data


class ListAdverseEvent:
    @staticmethod
    def list_adverse_event(filters, parameters, user_identity):
        data = AdverseEventService.list_adverse_event(filters, parameters, user_identity)
        return data