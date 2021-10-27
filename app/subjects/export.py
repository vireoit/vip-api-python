import tablib
import xlsxwriter
import pandas as pd

def export_table_data(data, pain_details, insights_data):
    df = pd.DataFrame(data)
    if pain_details:
        df2 = pd.DataFrame(pain_details)
        del df2['_id']
    else:
        df2 = ""
    del df['_id']
    if insights_data:
        df3 = pd.DataFrame(insights_data)
    else:
        df3 = ""
    with pd.ExcelWriter('subjects.xls') as writer:  
        df.to_excel(writer, sheet_name='Subjects', index=False)
        if pain_details:
            df2.to_excel(writer, sheet_name='Pain Details', index=False)
        if insights_data:
            df3.to_excel(writer, sheet_name='Personal Insights', index=False)
    file = pd.read_excel('subjects.xls')
    return file


def export_pain_data(data):
    df = pd.DataFrame(data)
    try:
        del df['_id']
    except:
        pass
    df.to_excel('pain_details.xls', index=False)
    file = pd.read_excel('pain_details.xls')
    return file
