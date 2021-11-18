import tablib
import xlsxwriter
import pandas as pd


def export_table_data(data):
    df = pd.DataFrame()
    with pd.ExcelWriter('survey_reports.xls') as writer:
        for key, values in data.items():
            df = pd.DataFrame(values)
            df.drop_duplicates(subset=['Subject Name' ,'Submitted Date'], inplace=True)  
            df.to_excel(writer, sheet_name=key, index=False)
    file = pd.read_excel('survey_reports.xls')
    return file
    