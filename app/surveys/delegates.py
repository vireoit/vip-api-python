from app.surveys.services import SurveyService


class SurveyDelegate:
    @staticmethod
    def export_survey_reports(filters,  parameters):
        data_file = SurveyService.export_survey_reports(filters, parameters)
        return data_file
