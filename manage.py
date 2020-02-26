import sys

import click
import logging

from infra.log import init_logger


@click.command()
@click.option('-i', '--indices', default='', help='Comma separated indices')
@click.option('-d', '--delete', is_flag=True, default=False, help='Delete indices')
def main(indices, delete):
    from infra._snapshot import ESClient

    client = ESClient()

    if delete:
        for index in indices.split(','):
            client.delete_index(index)
        raise SyntaxError('Missing action parameter')


if __name__ == '__main__':
    init_logger()
    try:
        main()
    except Exception as e:
        logging.exception('Failure')
        sys.exit(1)
