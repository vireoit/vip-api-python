import tablib
import xlsxwriter
import pandas as pd

def export_table_data(data, pain_details, insights_data, feedback_details, ae_list):
    if data:
        df = pd.DataFrame(data)
        del df['_id']
        if df.empty:
            data = ""
    else:
        df = ""
    if pain_details:
        df2 = pd.DataFrame(pain_details)
        del df2['_id']
        df2 = df2[['Subject Name', 'Submitted Date', 'Triggers', 'PainType', 'Medications', 'Sleep', 'Treatments', 
        'PainLocation', 'Feedback for vireo products', 'Notes']]
    else:
        df2 = ""
    if insights_data:
        df3 = pd.DataFrame(insights_data)
    else:
        df3 = ""
    if feedback_details:
        df4 = pd.DataFrame(feedback_details)
        df4.drop_duplicates(subset=['Subject Name' ,'Reported Date'], inplace=True)
    else:
        df4 = ""
    if ae_list:
        df5 = pd.DataFrame(ae_list)
        df5 = df5[['Subject Name', 'Reported Date', 'Event Type', 'Start Date', 'Ongoing or not', 'Any relation with cannabis product', 
        'Any treatment received for the event']]
    else:
        df5 = ""
    with pd.ExcelWriter('subjects.xls') as writer:
        if data:  
            df.to_excel(writer, sheet_name='Subjects', index=False)
        if pain_details:
            df2.to_excel(writer, sheet_name='Pain Details', index=False)
        if insights_data:
            df3.to_excel(writer, sheet_name='Personal Insights', index=False)
        if feedback_details:
            df4.to_excel(writer, sheet_name='Ratings and Feedback', index=False)
        if ae_list:
            df5.to_excel(writer, sheet_name='AE Logs', index=False)
    file = pd.read_excel('subjects.xls', engine='openpyxl')
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
