import tablib
import xlsxwriter
import pandas as pd

# with open('output.xls', 'wb') as f:
    #     f.write(data.export('xls'))
    #     print(f)


def export_table_data(data):
    df = pd.DataFrame(data)
    df.to_excel('subjects.xls', index=False)
    file = pd.read_excel('subjects.xls')
    return file