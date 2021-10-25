import tablib
import xlsxwriter
import pandas as pd

def export_table_data(data, pain_details):
    df = pd.DataFrame(data)
    df2 = pd.DataFrame(pain_details)
    del df['_id']
    del df2['_id']
    with pd.ExcelWriter('subjects.xls') as writer:  
        df.to_excel(writer, sheet_name='Subjects', index=False)
        df2.to_excel(writer, sheet_name='Pain Details', index=False)
    file = pd.read_excel('subjects.xls')
    return file


def export_pain_data(data):
    df = pd.DataFrame(data)
    del df['_id']
    df.to_excel('pain_details.xls', index=False)
    file = pd.read_excel('pain_details.xls')
    return file