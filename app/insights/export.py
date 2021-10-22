import tablib
import xlsxwriter
import pandas as pd


def export_table_data_personal(data):
    df = pd.DataFrame(data)
    df.to_excel('Insight-Personal-export.xls', index=False)
    file = pd.read_excel('Insight-Personal-export.xls')
    return file
    
def export_table_data_community(data):
    df = pd.DataFrame(data)
    df.to_excel('Insight-Community-export.xls', index=False)
    file = pd.read_excel('Insight-Community-export.xls')
    return file
