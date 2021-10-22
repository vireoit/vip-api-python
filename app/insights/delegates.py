from app.insights.services import InsightService, PainDetailGraphService
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


class PainDetailGraphDelegate:
    @staticmethod
    def pain_details_graph(filters, user_identity):
        data = PainDetailGraphService.pain_details_graph(filters, user_identity)
        return data
    