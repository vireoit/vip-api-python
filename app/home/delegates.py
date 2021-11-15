from app.home.services import PegScoreService, OnGoingFeedbackService, SatisfactionService, AdminHomeStatisticsService, \
    AdminHomeGraphService
from app.home.services import PegScoreService, OnGoingFeedbackService, SatisfactionService,\
    RewardRedemptionService, AdminHomeUserRatingsService



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
      

class AdminHomeDelegate:

    @staticmethod
    def get_admin_home_statistics(parameters):
        data = AdminHomeStatisticsService.get_admin_home_statistics(parameters)
        return data

    @staticmethod
    def get_admin_home_patients(parameters):
        data = AdminHomeGraphService.get_admin_home_patients(parameters)
        return data

    @staticmethod
    def get_admin_home_treatments(parameters, claims):
        data = AdminHomeGraphService.get_admin_home_treatments(parameters, claims)
        return data

    @staticmethod
    def get_admin_home_surveys(parameters):
        data = AdminHomeGraphService.get_admin_home_surveys(parameters)
        return data

    @staticmethod
    def get_admin_home_pain_type(parameters, claims):
        data = AdminHomeGraphService.get_admin_home_pain_type(parameters, claims)
        return data

class RewardRedemption:
    @staticmethod
    def list_accumulated_rewards(filters, user_identity):
        data = RewardRedemptionService.list_accumulated_reward_redemption(filters, user_identity)
        return data

class AdminHomeUserRatingsDelegate:
    @staticmethod
    def get_admin_home_user_ratings(parameters):
        data = AdminHomeUserRatingsService.get_admin_home_user_ratings(parameters)
        return data
       