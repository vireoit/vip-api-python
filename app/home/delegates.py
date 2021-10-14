from app.home.services import PegScoreService


class PegScoreDelegate:

    @staticmethod
    def create_peg_score_record(filters, user_identity):
        data = PegScoreService.create_peg_score_record(filters, user_identity)
        return data

    @staticmethod
    def peg_score_details(filters, user_identity):
        data = PegScoreService.peg_score_details(filters, user_identity)
        return data