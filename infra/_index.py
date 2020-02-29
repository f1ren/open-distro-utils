import re
from datetime import date, timedelta


def extract_month(index_name):
    return re.findall('\d\d\d\d-[0-2]\d', index_name)[0]


def filter_older_than(indices, month_ago):
    cursor = date.today()
    for i in range(month_ago):
        first = cursor.replace(day=1)
        cursor = first - timedelta(days=1)
    threshold_month_str = cursor.strftime("%Y-%m")
    return [i for i in indices if extract_month(i) < threshold_month_str]
