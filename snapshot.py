import sys

import click
import logging

from infra.consts import DEFAULT_ADMIN_CERT_PATH, DEFAULT_ADMIN_KEY_PATH
from infra.log import init_logger


@click.command()
# @click.option('-c', '--cert', default=DEFAULT_ADMIN_CERT_PATH, help='Admin certification path (e.g. {DEFAULT_ADMIN_CERT_PATH})')
# @click.option('-k', '--key', default=DEFAULT_ADMIN_KEY_PATH, help='Admin key path (e.g. {DEFAULT_ADMIN_KEY_PATH})')
@click.option('-f', '--first', default=None, help='First snapshot name')
@click.option('-l', '--last', default=None, help='Last snapshot name')
@click.option('-b', '--repo-bucket', default=None, help='Bucket name to register snapshot repository')
@click.option('-r', '--restore', default=None, help='Restore snapshot')
@click.option('-ls', '--list', is_flag=True, default=False, help='List snapshots')
@click.option('-d', '--delete', is_flag=True, default=False, help='Delete snapshots')
@click.option('-c', '--close-indices', is_flag=True, default=False, help='Close all indices')
@click.option('-o', '--open-indices', is_flag=True, default=False, help='Open all indices')
def main(first, last, repo_bucket, restore, list, delete, close_indices, open_indices):
    from infra._snapshot import SnapshotClient

    client = SnapshotClient()

    if repo_bucket is not None:
        client.create_repo(repo_bucket)
    elif list:
        client.list_snapshots()
    elif restore:
        client.restore(restore)
    elif delete:
        client.delete_multiple(first, last)
    elif close_indices:
        client.close_indices()
    elif open_indices:
        client.open_indices()
    else:
        raise SyntaxError('Missing action parameter')


if __name__ == '__main__':
    init_logger()
    try:
        main()
    except Exception as e:
        logging.exception('Failure')
        sys.exit(1)
