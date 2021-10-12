import tablib
import xlsxwriter
import pandas as pd


def export_table_data(data):
    df = pd.DataFrame(data)
    df.to_excel('subjects.xls', index=False)
    file = pd.read_excel('subjects.xls')
    return file