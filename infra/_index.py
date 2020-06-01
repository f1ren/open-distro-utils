from datetime import timedelta, datetime

from dateutil.parser import parse, ParserError


def _index_name_is_older_than(index_name, datetime_cursor):
    try:
        parsed_datetime = parse(index_name, fuzzy=True)
    except ParserError:
        return False

    return parsed_datetime <= datetime_cursor


def filter_older_than(indices, month_ago):
    cursor = datetime.utcnow()
    for i in range(month_ago):
        first = cursor.replace(day=1)
        cursor = first - timedelta(days=1)
    return [i for i in indices if _index_name_is_older_than(i, cursor)]
