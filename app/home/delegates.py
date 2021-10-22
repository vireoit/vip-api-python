from app.home.services import PegScoreService, OnGoingFeedbackService, SatisfactionService


class PegScoreDelegate:

    @staticmethod
    def create_peg_score_record(filters, user_identity):
        data = PegScoreService.create_peg_score_record(filters, user_identity)
        return data

    @staticmethod
    def peg_score_details(filters, user_identity):
        data = PegScoreService.peg_score_details(filters, user_identity)
        return data


class OnGoingFeedBack:
    @staticmethod
    def create_on_going_feedback(payload, user_identity):
        data = OnGoingFeedbackService.create_on_going_feedback(payload, user_identity)
        return data


class SatisfactionDelegate:

    @staticmethod
    def create_satisfaction_score_record(filters, user_identity):
        data = SatisfactionService.create_Satisfaction_score_record(filters, user_identity)
        return data

    @staticmethod
    def satisfaction_score_details(filters, user_identity):
        data = SatisfactionService.satisfaction_score_details(filters, user_identity)
        return data