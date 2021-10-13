

def format_cursor_obj(item):
    """ encode an single cursor object"""
    for key, value in item.items():
        if not isinstance(value, dict) or len(value) != 1:
            continue
        (subkey, subvalue), = value.items()
        if not subkey.startswith('$'):
            continue
        item[key] = subvalue
    return item
