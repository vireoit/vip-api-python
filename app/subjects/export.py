import tablib
import xlsxwriter
import pandas as pd

def export_table_data(data, pain_details):
    df = pd.DataFrame(data)
    if pain_details:
        df2 = pd.DataFrame(pain_details)
        del df2['_id']
    else:
        df2 = ""
    del df['_id']
    with pd.ExcelWriter('subjects.xls') as writer:  
        df.to_excel(writer, sheet_name='Subjects', index=False)
        if pain_details:
            df2.to_excel(writer, sheet_name='Pain Details', index=False)
    file = pd.read_excel('subjects.xls')
    return file


def export_pain_data(data):
    df = pd.DataFrame(data)
    del df['_id']
    df.to_excel('pain_details.xls', index=False)
    file = pd.read_excel('pain_details.xls')
    return file