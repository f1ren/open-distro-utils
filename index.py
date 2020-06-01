import sys

import click
import logging

from infra._index import filter_older_than
from infra.log import init_logger, info


@click.command()
@click.option('-i', '--indices', default=None, help='Comma separated indices')
@click.option('-p', '--pattern', default=None, help='Comma separated indices')
@click.option('-m', '--months-old', default=None, help='Number of months ago to limit indices')
@click.option('-d', '--delete', is_flag=True, default=False, help='Delete indices')
def main(indices, pattern, months_old, delete):
    from infra._es import ESClient

    client = ESClient()

    if indices:
        indices = indices.split(',')
    else:
        indices = client.list_indices(pattern)

    if months_old:
        months_ago = int(months_old)

        indices = filter_older_than(indices, months_ago)

    info('Matching indices', indices=', '.join(indices))

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
