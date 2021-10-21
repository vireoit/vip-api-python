from app.insights.services import InsightService
from app import response


class InsightDelegate:
    @staticmethod
    def export_personal_insights(parameters, user_identity):
        data = InsightService.export_personal_insights(parameters, user_identity)
        return data

    @staticmethod
    def export_community_insights(parameters, user_identity):
        data = InsightService.export_community_insights(parameters, user_identity)
        return data
        