import tablib
import xlsxwriter
import pandas as pd


def export_table_data(data):
    df = pd.DataFrame(data)
    df.drop_duplicates(subset='Subject Name', keep='first', inplace=True)
    df.to_excel('survey_reports.xls', index=False)
    file = pd.read_excel('survey_reports.xls')
    return file
    