import re
import sys
from datetime import datetime, date, timedelta

import click
import logging

from infra.log import init_logger, info


def extract_month(index_name):
    return re.findall('\d\d\d\d-[0-2]\d', index_name)[0]


def filter_older_than(indices, month_ago):
    cursor = date.today()
    for i in range(month_ago):
        first = cursor.replace(day=1)
        cursor = first - timedelta(days=1)
    threshold_month_str = cursor.strftime("%Y-%m")
    return [i for i in indices if extract_month(i) < threshold_month_str]


@click.command()
@click.option('-i', '--indices', default=None, help='Comma separated indices')
@click.option('-p', '--pattern', default=None, help='Comma separated indices')
@click.option('-m', '--months-old', default=None, help='Number of months ago to limit indices')
@click.option('-d', '--delete', is_flag=True, default=False, help='Delete indices')
def main(indices, pattern, months_old, delete):
    from infra._snapshot import ESClient

    client = ESClient()

    if indices:
        indices = indices.split(',')
    else:
        indices = client.list_indices(pattern)

    if months_old:
        months_ago = int(months_old)

        indices = filter_older_than(indices, months_ago)

    info('Working on', indices=', '.join(indices))

    if delete:
        if indices:
            for index in indices:
                client.delete_index(index)
        raise SyntaxError('Missing action parameter')


if __name__ == '__main__':
    init_logger()
    try:
        main()
    except Exception as e:
        logging.exception('Failure')
        sys.exit(1)
