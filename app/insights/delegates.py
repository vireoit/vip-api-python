from app.insights.services import PainDetailGraphService


class PainDetailGraphDelegate:
    @staticmethod
    def pain_details_graph(filters, user_identity):
        data = PainDetailGraphService.pain_details_graph(filters, user_identity)
        return data