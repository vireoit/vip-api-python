import tablib


def export_table_data(data):
    with open('output.xls', 'wb') as f:
        f.write(data.export('xls'))
